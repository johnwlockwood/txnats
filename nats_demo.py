
from sys import stdout
from sys import stderr
import logging
import json
from io import BytesIO
from collections import namedtuple

from zope.interface import Interface, Attribute

from txnats import NatsClient

from twisted.python import log

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


def my_on_msg(nats_client, data):
    stdout.write("yay\r\n")
    stdout.write(data)
    stdout.write("\r\n*")


@defer.inlineCallbacks
def somePubSubbing(nats_client):
    nats_client.ping()
    nats_client.sub("happy", 1)
    nats_client.unsub(1, 4)
    nats_client.pub("happy", "Hello Subber")
    nats_client.pub("happy", "How")
    nats_client.pub("happy", "Are")
    nats_client.pub("happy", "You?")
    nats_client.pub("happy", "Anyone listening?")
    yield reactor.callLater(60, nats_client.transport.loseConnection)


def main(reactor):

    host = "demo.nats.io"
    port = 4222

    point = TCP4ClientEndpoint(reactor, host, port)
    nats_client = NatsClient(verbose=False, on_msg=my_on_msg)
    nats_client.on_connect_d.addCallback(somePubSubbing)

    d = connectProtocol(point, nats_client)

    #d.addCallback(gotProtocol)
    return d

if __name__ == '__main__':
    log.startLogging(stderr, setStdout=0)
    main(reactor)
    reactor.run()

