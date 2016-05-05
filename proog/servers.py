"""
Servers for recieving stuff
"""

from aiosmtpd import smtp as aiosmtp, lmtp as aiolmtp
import asyncio


class SMTPError(Exception):
    def __init__(self, code, message):
        self.message = "{} {}".format(code, message)


class BaseServer:
    """Overrides some of aiosmtpd's SMTP class, but doesn't inherit from it yet
    so we can mix it up with the LMTP class too
    """

    _ehlo_features = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._ehlo_features is None:
            self._ehlo_features = []

        # XXX command_size_limits should go in EHLO?
        if self.data_size_limit:
            self._ehlo_features.append("SIZE %s" % self.data_size_limit)
            self.command_size_limits['MAIL'] += 26

        if not self._decode_data:
            self._ehlo_features.append("8BITMIME")

        # XXX command_size_limits should go in EHLO?
        if self.enable_SMTPUTF8:
            self._ehlo_features.append("SMTPUTF8")
            self.command_size_limits['MAIL'] += 10

    @asyncio.coroutine
    def smtp_EHLO(self, hostname):
        if not hostname:
            yield from self.push("501 Syntax: EHLO hostname")
            return
        if self.seen_greeting:
            yield from self.push("503 Duplicate HELO/EHLO")
            return

        self._set_rset_state()
        self.seen_greeting = hostname
        self.extended_smtp = True

        if self._ehlo_features:
            # list features
            yield from self.push("250-%s" % self.fqdn)
            for feature in self._ehlo_features[:-1]:
                yield from self.push("250-%s" % feature)

            # only the last line has a space between code and arg
            yield from self.push("250 %s" % self._ehlo_features[-1])
        else:
            # no features
            yield from self.push("250 %s" % self.fqdn)

    @asyncio.coroutine
    def smtp_HELP(self, arg):
        # disable HELP
        yield from self.push("500 Error: There's no help for you here")

    @asyncio.coroutine
    def smtp_RCPT(self, arg):
        # override aiosmptd's RCPT method so we can call our event_handler
        # XXX upstream bug as handlers should be able to do this already?
        if not self.seen_greeting:
            yield from self.push("503 Error: send HELO/EHLO first")
            return
        if not self.mailfrom:
            yield from self.push("503 Error: need MAIL command")
            return
        syntax_error = "501 Syntax: RCPT TO: <address>"
        if self.extended_smtp:
            syntax_error += " [<mail-parameters>]"
        if arg is None:
            yield from self.push(syntax_error)
            return

        arg = self._strip_command_keyword("TO:", arg)
        address, params = self._getaddr(self)
        params = self._getparams(params.upper().split())
        if not address:
            yield from self.push(syntax_error)
            return
        if not self.extended_smtp and params:
            yield from self.push(syntax_error)
            return
        if params is None:
            yield from self.push(syntax_error)
            return

        args = (self.peer, self.mailfrom, address)

        kwargs = {}
        if not self._decode_data:
            kwargs = {
                "mail_options": self.mail_options,
                "rcpt_options": params,
            }

        status = "250 OK"
        try:
            status = self.event_handler.check_rcpt(*args, **kwargs)
        except SMTPError as error:
            status = error.message
        else:
            self.rcpttos.append(address)
            self.rcpt_options = params
        self.push(status)


class AuthMixin:
    """Authentication mixin

    You probably want to combine this with ``StartTlsMixin``

    Exposes ``authenticated`` boolean. Defaults to ``False``.  Implements PLAIN
    and LOGIN only.
    """
    # XXX stub

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ehlo_features.append("AUTH PLAIN LOGIN")
        self.authenticated = None

    @asyncio.coroutine
    def smtp_AUTH(self, arg):
        # XXX authenticate!
        pass


class StartTlsMixin:
    """Mixin for STARTTLS support

    Exposes ``tls_started`` boolean. Defaults to ``False``
    """
    # XXX stub

    _tls_features = None

    def __init__(self, *args, **kwargs):
        # XXX my own mail server relpies with "250 DSN". Unsure about the significance of this
        if self._tls_features is None:
            self._tls_features = []

        super().__init__(*args, **kwargs)

        self._ehlo_features.append("STARTTLS")
        self.tls_started = False

    @asyncio.coroutine
    def smtp_STARTTLS(self, arg):
        if arg:
            yield from self.push("501 Syntax error (no parameters allowed)")
            return

        yield from self.push("220 Ready to start TLS")

        # XXX TLS magic goes here

        self.tls_started = True
        if self._tls_features:
            for feature in self._tls_features[:-1]:
                yield from self.push("250-%s" % feature)

            # only the last line has a space between code and arg
            yield from self.push("250 %s" % self._tls_features[-1])
        else:
            yield from self.push("250 OK")


class SMTP(BaseServer, aiosmtp.SMTP):
    pass


class LMTP(BaseServer, aiolmtp.LMTP):
    pass
