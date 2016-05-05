from functools import partial
import asyncio

from proog import servers, queues, clients


RELAY_QUEUE = None
LOCAL_QUEUE = None


class PublicService(servers.SMTP, servers.StartTlsMixin):
    """Service to be run on port 25, no AUTH."""
    pass


class SubmissionService(servers.SMTP, servers.StartTlsMixin, servers.AuthMixin):
    """Service to be run on port 587, requires AUTH and STARTTLS."""
    @asyncio.coroutine
    def smtp_MAIL(self, arg):
        if not self.authenticated:
            yield from self.push("530 Must issue a STARTTLS command first")
            return
        yield from super().smtp_MAIL(arg)

    @asyncio.coroutine
    def smpt_AUTH(self, arg):
        if not self.tls_started:
            yield from self.push("530 Must issue a STARTTLS command first")
            return
        yield from super().smtp_AUTH(arg)


class PublicHandler:
    """For use with ``PublicService``, only relays mail to local rcpttos"""
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        pass

    def check_rcpt(self, peer, mailfrom, address, **kwargs):
        pass


class SubmissionHandler:
    """For use with ``SubmissionService``, relays anyway as it assumes the
    connection has been authed
    """
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        pass

    def check_rcpt(self, peer, mailfrom, address, **kwargs):
        pass


def public():
    """Set up a server to listen on port 25"""
    loop = asyncio.get_event_loop()


def submission():
    """Set up a server to listen on port 587"""
    loop = asyncio.get_event_loop()


def relay():
    """Set up relay service"""
    global RELAY_QUEUE
    assert RELAY_QUEUE is None, "Don't call this, Twice"


def local():
    """Set up local delivery"""
    global LOCAL_QUEUE
    assert LOCAL_QUEUE is None, "Don't call this, Twice"
