#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import random
import string

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
import socket

responder_id = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="demo.nats.io",
                    help="IP of NATS server")
parser.add_argument("--port", default=4222,
                    help="port of NATS server")

parser.add_argument("--name", default="{} {}".format(responder_id,
                                                     socket.gethostname()),
                    help="Name of this client or device")

pargs = parser.parse_args()

led_grid_semaphore = defer.DeferredSemaphore(1)


@defer.inlineCallbacks
def show_msg(message):
    """
    Call the sense Hat's show message function in a thread
    because otherwise it would block the event loop.

    :param message: Message to display on the LED grid.
    """
    from sense_hat import SenseHat
    sense = SenseHat()
    yield deferToThread(
        sense.show_message, text_string=message,
        scroll_speed=0.10, text_colour=(50, 100, 40))


@defer.inlineCallbacks
def respond_on_msg(nats_protocol, sid, subject, reply_to, payload):
    """
    Run show_msg with the semaphore that allows only one
    message to be shown at a time.

    """
    yield led_grid_semaphore.run(show_msg, payload.decode())
    if reply_to:
        nats_protocol.pub(
            reply_to,
            "Message diplayed by {}!".format(pargs.name).encode())


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
    create_client(reactor, pargs.host, pargs.port)

if __name__ == '__main__':
    globalLogPublisher.addObserver(simpleObserver)
    main(reactor)
    reactor.run()

