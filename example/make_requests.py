#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from sys import stderr
import random
import string

import txnats

from twisted.python import log

from twisted.internet import defer
from twisted.internet import task
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


client_id = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def sid_on_msg(nats_protocol, sid, subject, reply_to, payload):
    stdout.write("sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(payload)
    stdout.write("\r\n*")


@defer.inlineCallbacks
def someRequests(nats_protocol):
    """
    The only point of this code is to show some basic subscribing
    and publishing.
    """
    client_inbox = "inbox_{}".format(client_id)
    nats_protocol.sub(client_inbox, 1, on_msg=sid_on_msg)
    for x in range(100):
        nats_protocol.pub("a-queue", "Do something! {}".format(x),
                          client_inbox)

    # Lose the connection one second after the "and another thing" msg.
    yield task.deferLater(nats_protocol.reactor,
                          10, nats_protocol.transport.loseConnection)

    # stop the reactor(the event loop) one second after that.
    yield task.deferLater(nats_protocol.reactor, 1, reactor.stop)


def main(reactor):

    host = "demo.nats.io"
    port = 4222

    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(
        verbose=False,
        on_connect=someRequests)

    d = connectProtocol(point, nats_protocol)

    # Log if there is an error making the connection.
    d.addErrback(log.msg)
    # Log what is returned by the connectProtocol.
    d.addCallback(log.msg)

    return d

if __name__ == '__main__':
    log.startLogging(stderr, setStdout=0)
    main(reactor)
    reactor.run()

