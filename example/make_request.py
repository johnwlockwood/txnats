#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
import random
import string

import txnats

from twisted.logger import globalLogPublisher
from simple_log_observer import simpleObserver

from twisted.logger import Logger
log = Logger()

from twisted.internet import defer
from twisted.internet import task
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol

from txnats import actions

def event_subscriber(event):
    if isinstance(event, actions.SendConnect):
        log.info("got connect")
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

@defer.inlineCallbacks
def someRequests(nats_protocol):
    """
    The only point of this code is to show some basic subscribing
    and publishing.
    """
    log.info("about to request")
    d = nats_protocol.request("ssshh", "Boo")
    d.addErrback(lambda np: log.info("{p}", p=np))
    # Log what is returned by the connectProtocol.
    d.addCallback(lambda np: log.info("{p}", p=np))
    log.info("response : {}".format("dd"))

    # Lose the connection one second after the "and another thing" msg.
    yield task.deferLater(nats_protocol.reactor,
                          10, nats_protocol.transport.loseConnection)

    # stop the reactor(the event loop) one second after that.
    yield task.deferLater(nats_protocol.reactor, 0, reactor.stop)


def main(reactor):

    host = "demo.nats.io"
    port = 4222

    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(
        verbose=True,
        event_subscribers=[
                event_subscriber
            ],
        on_connect=someRequests)

    connecting = connectProtocol(point, nats_protocol)
    # Log if there is an error making the connection.
    connecting.addErrback(lambda np: log.info("{p}", p=np))
    # Log what is returned by the connectProtocol.
    connecting.addCallback(lambda np: log.info("{p}", p=np))
    return connecting


if __name__ == '__main__':
    globalLogPublisher.addObserver(simpleObserver)
    main(reactor)
    reactor.run()

