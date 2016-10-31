#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout

import txnats

from twisted.logger import globalLogPublisher
from simple_log_observer import simpleObserver
from twisted.logger import Logger
log = Logger()

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


def on_happy_msg(nats_protocol, sid, subject, reply_to, payload):
    stdout.write(
        "sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(payload.decode())
    stdout.write("\r\n*")


def create_client(reactor, host, port):
    """
    Start a Nats Protocol and connect it to a NATS endpoint over TCP4
    which subscribes to a subject.

    Reconnect and resubscribe.
    """
    log.info("Start client.")
    point = TCP4ClientEndpoint(reactor, host, port)

    def event_subscriber(event):
        if event["type"] == txnats.io.CONNECT:
            event["protocol"].sub("happy", 6, on_msg=on_happy_msg)
        elif event["type"] == txnats.io.CONNECTION_LOST:
            # MAYBE defer reconnecting with a backoff
            connecting = connectProtocol(
                point, txnats.io.NatsProtocol(
                    verbose=False, event_subscribers=event["protocol"].event_subscribers))
            # Log if there is an error making the connection.
            connecting.addErrback(lambda np: log.info("{p}", p=np))
            # Log what is returned by the connectProtocol.
            connecting.addCallback(lambda np: log.info("{p}", p=np))

    # Because NatsProtocol implements the Protocol interface, Twisted's
    # connectProtocol knows how to connected to the endpoint.
    connecting = connectProtocol(
        point, txnats.io.NatsProtocol(
            verbose=False, event_subscribers=[event_subscriber]))
    # Log if there is an error making the connection.
    connecting.addErrback(lambda np: log.info("{p}", p=np))
    # Log what is returned by the connectProtocol.
    connecting.addCallback(lambda np: log.info("{p}", p=np))


def main(reactor):
    host = "demo.nats.io"
    port = 4222
    create_client(reactor, host, port)

if __name__ == '__main__':
    globalLogPublisher.addObserver(simpleObserver)
    main(reactor)
    reactor.run()

