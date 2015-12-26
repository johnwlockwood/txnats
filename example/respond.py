#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from sys import stderr

import txnats

from twisted.python import log

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


def respond_on_msg(nats_protocol, sid, subject, reply_to, payload):
    """
    Write the message information to standard out, and if
    there is a reply_to, publish a message to it.
    """
    stdout.write("sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(payload)
    stdout.write("\r\n*")
    if reply_to:
        nats_protocol.pub(reply_to, "Roger!")


def listen(nats_protocol):
    """
    When the protocol is first connected, make a subscription.
    """
    log.msg("HELLO LISTEN")

    nats_protocol.sub("ssshh", 6, on_msg=respond_on_msg)


def create_client(reactor, host, port):
    """
    Start a Nats Protocol and connect it to a NATS endpoint over TCP4
    which subscribes a subject with a callback that sends a response
    if it gets a reply_to.
    """
    log.msg("Start client.")
    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(verbose=False, on_connect=listen)

    connecting = connectProtocol(point, nats_protocol)
    # Log if there is an error making the connection.
    connecting.addErrback(log.msg)
    # Log what is returned by the connectProtocol.
    connecting.addCallback(log.msg)
    return connecting


def main(reactor):

    host = "demo.nats.io"
    port = 4222

    create_client(reactor, host, port)

if __name__ == '__main__':
    log.startLogging(stderr, setStdout=0)
    main(reactor)
    reactor.run()

