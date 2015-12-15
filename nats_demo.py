from sys import stdout
from sys import stderr

import txnats

from twisted.python import log

from twisted.internet import defer
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
    nats_protocol.ping()
    nats_protocol.sub("happy", 1)
    nats_protocol.sub("lucky", 2, on_msg=sid_on_msg)
    nats_protocol.unsub(1, 4)
    nats_protocol.pub("happy", "Hello Subber")
    nats_protocol.pub("happy", "How")
    nats_protocol.pub("lucky", "Spin To")
    nats_protocol.pub("happy", "Are")
    nats_protocol.pub("happy", "You?")
    nats_protocol.pub("happy", "Anyone listening?")
    nats_protocol.pub("lucky", "WIN!!!", "gimmie")
    nats_protocol.reactor.callLater(1, nats_protocol.pub, "lucky",
                                    "and another thing", "gimmie")
    yield nats_protocol.reactor.callLater(
        3, nats_protocol.transport.loseConnection)
    reactor.callLater(3.1, reactor.stop)


def main(reactor):

    host = "demo.nats.io"
    port = 4222

    # TODO: make a NatsClient that does this, choosing the proper endpoint
    point = TCP4ClientEndpoint(reactor, host, port)
    nats_protocol = txnats.io.NatsProtocol(verbose=False, on_msg=my_on_msg)
    nats_protocol.on_connect_d.addCallback(somePubSubbing)

    d = connectProtocol(point, nats_protocol)

    return d

if __name__ == '__main__':
    log.startLogging(stderr, setStdout=0)
    main(reactor)
    reactor.run()

