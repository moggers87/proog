"""
Servers for recieving stuff
"""

import asyncio
import aiosmtpd


class SMTPError(Exception):
    def __init__(self, code, message):
        self.message = "{} {}".format(code, message)


class BaseServer:
    """Overrides some of aiosmtpd's SMTP class, but don't inherit from it yet
    so we can mix it up with the LMTP class too"""

    _ehlo_features = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._ehlo_features is None:
            self._ehlo_features = []

        # XXX command_size_limits should go in EHLO?
        if self.data_size_limit:
            self._ehlo_features.append("SIZE %s"% self.data_size_limit)
             self.command_size_limits['MAIL'] += 26

        if not self._decode_data:
            self._ehlo_features.append("8BITMIME"])

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
                yield from self.push("250-%s" % self.fqdn)

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
            yield from sef.push("503 Error: send HELO/EHLO first")
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
        if not address:
            yield from self.push(syntax_error)
            return
        if not self.extended_smtp and params:
            yield from self.push(syntax_error)
            return

        status = "250 OK"
        try:
            status = self.event_handler.check_rcpt(address, params)
        except SMTPError as error:
            status = error.message
        else:
            self.rcpttos.append(address)
        self.push(status)


class AuthMixin:
    # XXX stub
    # XXX how should this work with STARTTLS? e.g. auth only available tls?

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ehlo_features.append("AUTH PLAIN LOGIN")

    @asyncio.coroutine
    def smtp_AUTH(self, arg):
        pass


class StartTlsMixin:
    # XXX stub

    _tls_features = None

    def __init__(self, *args, **kwargs):
        if self._tls_features is None:
            self._tls_features = []

        super().__init__(*args, **kwargs)

        self._ehlo_features.append("STARTTLS")
        self.tls_started = False

    @asyncio.coroutine
    def smtp_STARTTLS(self, arg):
        self.push("220 Ready to start TLS")

        # XXX TLS magic goes here


class SMTP(BaseServer, aiosmtpd.SMTP):
    pass


class LMTP(BaseServer, aiosmtpd.LMTP):
    pass


class SMTPWithAuth(AuthMixin, SMTP):
    pass
