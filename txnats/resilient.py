from __future__ import absolute_import

from twisted.internet import defer
from twisted.internet.endpoints import connectProtocol
from twisted.internet import error
from twisted.logger import Logger
log = Logger()

from .protocol import NatsProtocol
from . import actions


def sleep(own_reactor, seconds):
    d = defer.Deferred()
    own_reactor.callLater(seconds, d.callback, seconds)
    return d


@defer.inlineCallbacks
def connect(point, protocol, backoff, max_retries=100):
    while backoff.retries <= max_retries:
        log.debug("tries {}".format(backoff.retries))
        log.debug("connecting..")
        try:
            yield connectProtocol(point, protocol)
            backoff.reset_delay()
            log.debug(".connected")
            defer.returnValue(None)
        except (error.ConnectError, error.DNSLookupError):
            delay = backoff.get_delay()
            log.debug("connection failed, sleep for {}".format(delay))
            log.error()
            yield sleep(protocol.reactor, delay)


def make_reconnector(point, backoff, max_retries=100):
    """
    Makes and returns an event subscriber function that, in the event of
    a disconnect, it calls this module's connect function.
    """
    def reconnector(event):
        if isinstance(event, actions.ConnectionLost):
            if event.protocol.ping_loop.running:
                event.protocol.ping_loop.stop()
            if not event.reason.check(error.ConnectionDone):
                protocol = NatsProtocol(
                    own_reactor=event.protocol.reactor,
                    verbose=event.protocol.verbose, 
                    pedantic=event.protocol.client_info.pedantic,
                    ssl_required=event.protocol.client_info.ssl_required,
                    auth_token=event.protocol.client_info.auth_token,
                    user=event.protocol.client_info.user,
                    password=event.protocol.client_info.password,
                    on_msg=event.protocol.on_msg,
                    #on_connect=event.protocol.on_connect,
                    event_subscribers=event.protocol.event_subscribers, 
                    subscriptions=event.protocol.subscriptions,
                    unsubs=event.protocol.unsubs)
                connect(point, protocol, backoff, max_retries)
    return reconnector


def ping_loop_controller(event):
    """
    Upon connect, it starts the ping loop and upon disconnect,
    stops the ping loop.
    """
    if isinstance(event, actions.SendConnect):
        if not event.protocol.ping_loop.running:
            event.protocol.ping_loop.start(10, now=True)
    elif isinstance(event, (actions.Disconnected, actions.ConnectionLost)):
        if event.protocol.ping_loop.running:
            event.protocol.ping_loop.stop()
