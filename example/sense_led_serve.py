#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
import random
import string
from sense_hat import SenseHat

import txnats

from twisted.logger import globalLogPublisher
from simple_log_observer import simpleObserver
from twisted.logger import Logger
log = Logger()

from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol

responder_id = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

sem = defer.DeferredSemaphore(1)
sense = SenseHat()


@defer.inlineCallbacks
def show_msg(message):
    yield deferToThread(
        sense.show_message, text_string=message,
        scroll_speed=0.10, text_colour=(50, 100, 40))


@defer.inlineCallbacks
def respond_on_msg(nats_protocol, sid, subject, reply_to, payload):
    """
    Write the message payload to standard out, and if
    there is a reply_to, publish a message to it.
    """
    yield sem.run(show_msg, payload.decode())
    if reply_to:
        nats_protocol.pub(reply_to, "Roger, from {}!".format(responder_id))


def listen(nats_protocol):
    """
    When the protocol is first connected, make a subscription.
    """
    nats_protocol.sub("senseshow", 1,
                      on_msg=respond_on_msg)


def create_client(reactor, host, port):
    """
    Start a Nats Protocol and connect it to a NATS endpoint over TCP4
    which subscribes a subject with a callback that sends a response
    if it gets a reply_to.
    """
    log.info("Start client.")
    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(verbose=False, on_connect=listen)

    # Because NatsProtocol implements the Protocol interface, Twisted's
    # connectProtocol knows how to connected to the endpoint.
    connecting = connectProtocol(point, nats_protocol)
    # Log if there is an error making the connection.
    connecting.addErrback(lambda np: log.info("{p}", p=np))
    # Log what is returned by the connectProtocol.
    connecting.addCallback(lambda np: log.info("{p}", p=np))
    return connecting


def main(reactor):

    host = "demo.nats.io"
    host = "192.168.86.160"
    port = 4222

    create_client(reactor, host, port)

if __name__ == '__main__':
    globalLogPublisher.addObserver(simpleObserver)
    main(reactor)
    reactor.run()

