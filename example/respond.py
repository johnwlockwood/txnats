#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from sys import stderr

import txnats

from twisted.python import log

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


def respond_on_msg(nats_protocol, sid, subject, reply_to, data):
    stdout.write("sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(data)
    stdout.write("\r\n*")
    if reply_to:
        nats_protocol.pub(reply_to, "Roger!")


def listen(nats_protocol):
    """
    Just subscribe to a subject.
    """
    log.msg("HELLO LISTEN")

    nats_protocol.sub("ssshh", 6, on_msg=respond_on_msg)


def second_client(reactor, host, port):

    log.msg("start second client")
    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(verbose=False)
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

