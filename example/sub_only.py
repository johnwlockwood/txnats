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


def boo_on_msg(nats_protocol, data):
    stdout.write("boo\r\n")
    stdout.write(data)
    stdout.write("oob\r\n*")


def different_on_msg(nats_protocol, sid, subject, reply_to, data):
    stdout.write("BEEEEPPPE Just listening sid: {}, subject: {}, reply-to: {}\r\n".format(
                    sid, subject, reply_to))
    stdout.write(data)
    stdout.write("\r\n*")


def listen(nats_protocol):
    """
    Just subscribe to a subject.
    """
    log.msg("HELLO LISTEN")

    nats_protocol.sub("happy", 6, on_msg=different_on_msg)


def second_client(reactor, host, port):

    log.msg("start second client")
    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(verbose=False, on_msg=boo_on_msg)
    nats_protocol.on_connect_d.addCallback(listen)
    d = connectProtocol(point, nats_protocol)

    # Log if there is an error making the connection.
    d.addErrback(log.msg)
    # Log what is returned by the connectProtocol.
    d.addCallback(log.msg)

    return d


def main(reactor):

    host = "demo.nats.io"
    port = 4222

    second_client(reactor, host, port)

if __name__ == '__main__':
    log.startLogging(stderr, setStdout=0)
    main(reactor)
    reactor.run()

