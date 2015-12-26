#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from sys import stderr

import txnats

from twisted.python import log

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


def different_on_msg(nats_protocol, sid, subject, reply_to, payload):
    stdout.write(
        "BEEEEPPPE listening sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(payload)
    stdout.write("\r\n*")


def listen(nats_protocol):
    """
    Just subscribe to a subject.
    """
    log.msg("HELLO LISTEN")

    nats_protocol.sub("happy", 6, on_msg=different_on_msg)


def create_client(reactor, host, port):
    """
    Start a Nats Protocol and connect it to a NATS endpoint over TCP4
    which subscribes to a subject.
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

