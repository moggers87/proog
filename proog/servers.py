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

    @asyncio.coroutine
    def smtp_HELP(self, arg):
        # disable HELP
        yield from self.push("500 Error: There's no help for you here")

    @asyncio.coroutine
    def smtp_RCPT(self, arg):
        # override aiosmptd's RCPT method so we can call our event_handler
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
        finally:
            self.push(status)


class AuthMixin:
    # XXX stub

    @asyncio.coroutine
    def smtp_EHLO(self):
        super().smtp_EHLO()
        self.push("250 AUTH")


class SMTP(BaseServer, aiosmtpd.SMTP):
    pass


class LMTP(BaseServer, aiosmtpd.LMTP):
    pass


class SMTPWithAuth(AuthMixin, SMTP):
    pass
