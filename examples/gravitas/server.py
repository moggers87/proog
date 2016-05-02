from functools import partial
import asyncio

from proog import servers, queues, clients


RELAY_QUEUE = None
LOCAL_QUEUE = None


class PublicService(servers.BaseServer, servers.StartTlsMixin):
    pass


class SubmissionService(servers.BaseServer, servers.StartTlsMixin, servers.AuthMixin):
    @asyncio.coroutine
    def smtp_MAIL(self, arg):
        if not self.authenticated:
            yield from self.push("503 Authenticate first")
            return
        yield from super().smtp_MAIL(arg)

    @asyncio.coroutine
    def smpt_AUTH(self, arg):
        if not self.tls_started:
            yield from self.push("503 STARTTLS first")
            return
        yield from super().smtp_AUTH(arg)


class PublicHandler:
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        pass

    def check_rcpt(self, peer, mailfrom, address, **kwargs):
        pass


class SubmissionHandler:
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
