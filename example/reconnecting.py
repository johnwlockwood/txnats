#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout

import txnats
from txnats import actions
from txnats import resilient

from twisted.internet import defer
from twisted.logger import globalLogPublisher
from twisted.internet import protocol
from simple_log_observer import simpleObserver
from twisted.logger import Logger
log = Logger()

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import error


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
    nats_protocol.pub("happy", "Still There?".encode())
    log.info("mark unsub")


def event_subscriber(event):
    if isinstance(event, actions.SendConnect):
        log.info("got connect")
        event.protocol.apply_subscriptions()
    elif isinstance(event, actions.ReceivedInfo):
        log.info("got info")
    elif isinstance(event, actions.SendSub):
        log.info("got sub sid: {}".format(event.sid))
    elif isinstance(event, actions.UnsubMaxReached):
        log.info("done subscription: {}".format(event.sid))
    elif isinstance(event, actions.SendUnsub):
        log.info("Unsub requested {}".format(event))
    elif isinstance(event, actions.ReceivedPing):
        log.info("got Ping")
    elif isinstance(event, actions.ReceivedPong):
        log.info("got Pong outstanding: {}".format(event.outstanding_pings))
    elif isinstance(event, actions.SendPing):
        log.info("Sending Ping outstanding: {}".format(event.outstanding_pings))
    elif isinstance(event, actions.SendPong):
        log.info("Sending Pong")
    elif isinstance(event, actions.Disconnected):
        log.info("disconnect")

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

    # Because NatsProtocol implements the Protocol interface, Twisted's
    # connectProtocol knows how to connected to the endpoint.
    return resilient.connect(
        point, 
        txnats.io.NatsProtocol(
            verbose=True, 
            event_subscribers=[
                resilient.make_reconnector(point, backoff),
                resilient.ping_loop_controller,
                event_subscriber
            ],
            on_connect=someRequests, 
            subscriptions=subscriptions), 
        backoff)


def main(reactor):
    host = "demo.nats.io"
    port = 4222
    create_client(reactor, host, port)

if __name__ == '__main__':
    globalLogPublisher.addObserver(simpleObserver)
    main(reactor)
    reactor.run()
