#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout

import txnats
from txnats import actions

from twisted.internet import defer
from twisted.logger import globalLogPublisher
from twisted.internet import protocol
from simple_log_observer import simpleObserver
from twisted.logger import Logger
log = Logger()

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol
from twisted.internet import error


def sleep(own_reactor, seconds):
    d = defer.Deferred()
    own_reactor.callLater(seconds, d.callback, seconds)
    return d


def on_happy_msg(nats_protocol, sid, subject, reply_to, payload):
    stdout.write(
        "sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(payload.decode())
    stdout.write("\r\n*")


@defer.inlineCallbacks
def someRequests(nats_protocol):
    """
    Unsubscribe sid 6 once one message is received.
    """
    yield
    nats_protocol.unsub("6", 1)
    nats_protocol.pub("happy", "Hello Subber".encode())
    log.info("mark unsub")

@defer.inlineCallbacks
def resilient_connect(point, protocol, backoff):
    while backoff.retries < 100:
        log.info("tries {}".format(backoff.retries))
        log.info("connecting..")
        try:
            yield connectProtocol(point, protocol)
            backoff.reset_delay()
            log.info(".connected")
            defer.returnValue(None)
        except (error.ConnectError, error.DNSLookupError):
            delay = backoff.get_delay()
            log.info("connection failed, sleep for {}".format(delay))
            log.error()
            yield sleep(protocol.reactor, delay)

def create_client(reactor, host, port):
    """
    Start a Nats Protocol and connect it to a NATS endpoint over TCP4
    which subscribes to a subject.

    Reconnect and resubscribe.
    """
    log.info("Start client.")
    point = TCP4ClientEndpoint(reactor, host, port)
    backoff = txnats.Backoff()
    subscriptions = {
        "6": txnats.config_state.SubscriptionArgs(subject="happy", sid="6", on_msg=on_happy_msg)
        }
            
    def event_subscriber(event):
        if isinstance(event, actions.SendConnect):
            log.info("got connect")
            for sid, sub in subscriptions.items():
                event.protocol.sub(sub.subject, sid, sub.queue_group, sub.on_msg)
                if sid in event.protocol.unsubs:
                    log.info("unsubscribing sid: {} with max_msgs: {}".format(sid, event.protocol.unsubs[sid]))
                    event.protocol.unsub(sid, max_msgs=event.protocol.unsubs[sid])
            event.protocol.ping_loop.start(10, now=True)
        elif isinstance(event, actions.ReceivedInfo):
            log.info("got info")
        elif isinstance(event, actions.SendSub):
            log.info("got sub sid: {}".format(event.sid))
            subscriptions[event.sid]=txnats.config_state.SubscriptionArgs(
                subject=event.subject,
                sid=event.sid,
                queue_group=event.queue_group,
                on_msg=event.on_msg)
        elif isinstance(event, actions.UnsubMaxReached):
            log.info("done subscription: {}".format(event.sid))
            del subscriptions[event.sid]
        elif isinstance(event, actions.SendUnsub):
            log.info("Unsub requested {}".format(event))
        elif isinstance(event, actions.ReceivedPing):
            log.info("got Ping")
        elif isinstance(event, actions.ReceivedPong):
            log.info("got Pong outstanding: {}".format(event.outstanding_pings))
        elif isinstance(event, actions.SendPing):
            log.info("Sending Ping outstanding: {}".format(event.outstanding_pings))
            if event.outstanding_pings > 3:
                log.info("Preemptivly disconnecting")
                event.protocol.transport.loseConnection()
        elif isinstance(event, actions.SendPong):
            log.info("Sending Pong")
        elif isinstance(event, actions.Disconnected):
            log.info("disconnect")
            if event.protocol.ping_loop.running:
                event.protocol.ping_loop.stop()
        elif isinstance(event, actions.ConnectionLost):
            log.info("connection lost {}".format(event.reason))
            if event.protocol.ping_loop.running:
                log.info("stop pinging")
                event.protocol.ping_loop.stop()
            if not event.reason.check(error.ConnectionDone):
                protocol = txnats.io.NatsProtocol(
                    verbose=True, 
                    event_subscribers=event.protocol.event_subscribers, 
                    unsubs=event.protocol.unsubs)
                resilient_connect(point, protocol, backoff)

    # Because NatsProtocol implements the Protocol interface, Twisted's
    # connectProtocol knows how to connected to the endpoint.
    return resilient_connect(
        point, 
        txnats.io.NatsProtocol(
            verbose=True, 
            event_subscribers=[event_subscriber], on_connect=someRequests), 
        backoff)


def main(reactor):
    host = "demo.nats.io"
    port = 4222
    create_client(reactor, host, port)

if __name__ == '__main__':
    globalLogPublisher.addObserver(simpleObserver)
    main(reactor)
    reactor.run()
