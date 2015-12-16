#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from sys import stderr

import txnats

from twisted.python import log

from twisted.internet import defer
from twisted.internet import task
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


def my_on_msg(nats_protocol, data):
    stdout.write("yay\r\n")
    stdout.write(data)
    stdout.write("\r\n*")


def sid_on_msg(nats_protocol, sid, subject, reply_to, data):
    stdout.write("sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(data)
    stdout.write("\r\n*")


@defer.inlineCallbacks
def somePubSubbing(nats_protocol):
    """
    The only point of this code is to show some basic subscribing
    and publishing.
    """
    host = "demo.nats.io"
    port = 4222
    nats_protocol.ping()
    nats_protocol.sub("happy", 1)

    # sid_on_msg will be called when a message comes in on sid 2.
    nats_protocol.sub("lucky", 2, on_msg=sid_on_msg)

    # subscribe to a wildcard subject, associating it with sid 3 using the same
    # sid_on_msg callback.
    nats_protocol.sub("smile.*", 3, on_msg=sid_on_msg)
    nats_protocol.unsub(1, 4)
    nats_protocol.pub("happy", "Hello Subber")
    nats_protocol.pub("happy", "How")
    nats_protocol.pub("lucky", "Spin To")
    nats_protocol.pub("happy", "Are")
    nats_protocol.pub("happy", "You?")

    nats_protocol.pub("smile.sfas", "WHat!")

    nats_protocol.pub("happy", "Anyone listening?")

    nats_protocol.pub("lucky", "WIN!!!", "smile12")

    # After some time, publish some more messages
    d = task.deferLater(nats_protocol.reactor, 0.5,
                        nats_protocol.pub, "lucky",
                        "heya", "gimmie")
    yield d

    # This will publish a message four seconds after the one above because of
    # this function being decorated with inlineCallbacks.
    yield task.deferLater(nats_protocol.reactor,
                          4, nats_protocol.pub, "lucky",
                          "and another thing", "gimmie")

    nats_protocol.sub("inbox123", 4, on_msg=sid_on_msg)
    nats_protocol.unsub(4, 1)
    nats_protocol.pub("ssshh", "Any one there?!!!", "inbox123")

    # Lose the connection one second after the "and another thing" msg.
    yield task.deferLater(nats_protocol.reactor,
                          1, nats_protocol.transport.loseConnection)

    # stop the reactor(the event loop) one second after that.
    yield task.deferLater(nats_protocol.reactor, 1, reactor.stop)


def main(reactor):

    host = "demo.nats.io"
    port = 4222

    # TODO: make a NatsClient that does this, choosing the proper endpoint

    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(verbose=False, on_msg=my_on_msg)

    # Add a callback for after the TCP connection is made and the protocol has
    # received the nats server INFO and sent a CONNECT with the client info.
    # In this example, call our function above to do some subscribing and
    # publishing of messages.
    nats_protocol.on_connect_d.addCallback(somePubSubbing)

    # Because NatsProtocol implements the Protocol interface, Twisted's
    # connectProtocol knows how to connected to the endpoint.
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

