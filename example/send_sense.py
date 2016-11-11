#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
import argparse
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


client_id = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="demo.nats.io",
                    help="IP of NATS server")
parser.add_argument("--port", default=4222,
                    help="port of NATS server")

parser.add_argument('messages', metavar='M', type=str, nargs='+',
                    help='Messages to send')

pargs = parser.parse_args()


def sid_on_msg(nats_protocol, sid, subject, reply_to, payload):
    stdout.write("sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(payload.decode())
    stdout.write("\r\n*")


def sleep(own_reactor, seconds):
    """A sleep function that won't block the event loop."""
    d = defer.Deferred()
    own_reactor.callLater(seconds, d.callback, seconds)
    return d


@defer.inlineCallbacks
def someRequests(nats_protocol):
    """
    The only point of this code is to show some basic subscribing
    and publishing.
    """
    client_inbox = "inbox_{}".format(client_id)
    nats_protocol.sub(client_inbox, "1", on_msg=sid_on_msg)
    if pargs.messages:
        for x in pargs.messages:
            nats_protocol.pub("senseshow",
                              "{}".format(x).encode(),
                              client_inbox)
            log.info("sent: {}".format(x))
            yield sleep(nats_protocol.reactor, 0.01)

    # Wait for 10 seconds, then lose the connection.
    # TODO: A more sophisticated thing would be to track the responses.
    yield task.deferLater(nats_protocol.reactor, 10,
                          nats_protocol.transport.loseConnection)

    # stop the reactor(the event loop) one second after that.
    yield task.deferLater(nats_protocol.reactor, 1, reactor.stop)


def main(reactor):

    point = TCP4ClientEndpoint(reactor, pargs.host, pargs.port)
    nats_protocol = txnats.io.NatsProtocol(
        verbose=False,
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

