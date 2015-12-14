import json
from sys import stdout

from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


VERSION = 0.1
LANG = "English"
CLIENT_NAME = "xnats"


class NatsClient(Protocol):
    def dataReceived(self, data):
        stdout.write(data)

    def connect(self, verbose=True, pedantic=False,
                ssl_required=False, auth_token=None, user="",
                password=""):
        """
        Tell the NATS server about this client and it's options.

        @param verbose: Turns on +OK protocol acknowledgements.
        @param pedantic: Turns on additional strict format checking, e.g.
         for properly formed subjects
        @param ssl_required: Indicates whether the client requires
         an SSL connection.
        @param auth_token: Client authorization token
        @param user: Connection username (if auth_required is set)
        @param pass: Connection password (if auth_required is set)
        """
        options = {
            "verbose": verbose,
            "pedantic": pedantic,
            "ssl_required": ssl_required,
            "auth_token": auth_token,
            "user": user,
            "pass": password,
            "name": CLIENT_NAME,
            "lang": LANG,
            "version": VERSION,
        }
        self.transport.write(b"CONNECT {}".format(json.dumps(options)))

    def pub(self, subject,  payload, reply_to=""):
        """
        Publish a payload of bytes to a subject.

        @param subject: The destination subject to publish to.
        @param reply_to: The reply inbox subject that subscribers can use
         to send a response back to the publisher/requestor.
        @param payload: The message payload data, in bytes.
        """
        reply_part = b""
        if reply_to:
            reply_part = b"{} ".format(reply_to)

        self.transport.write(b"PUB {} {}{}\r\n{}\r\n".format(
            subject, reply_part, len(payload), payload))

    def sub(self, subject, sid, queue_group=None):
        """
        Subscribe to a subject.

        @param subject: The subject name to subscribe to.
        @param sid: A unique alphanumeric subscription ID.
        @param queue_group: If specified, the subscriber will
         join this queue group.
        """
        queue_group_part = b""
        if queue_group:
            queue_group_part = b"{} ".format(queue_group)

        self.transport.write(b"SUB {} {}{}\r\n".format(
            subject, sid, queue_group_part))

    def unsub(self, sid, max_msgs=None):
        """
        Unsubcribes the connection from the specified subject,
        or auto-unsubscribes after the specified
        number of messages has been received.

        @param sid: The unique alphanumeric subscription ID of
         the subject to unsubscribe from.
        @param max_msgs: Number of messages to wait for before
         automatically unsubscribing.
        """
        max_msgs_part = b""
        if max_msgs:
            max_msgs_part = b"{}".format(max_msgs)

        self.transport.write(b"UNSUB {} {}\r\n".format(sid, max_msgs_part))


def gotProtocol(p):
    p.connect()
    reactor.callLater(1, p.sub, "happy", 1)
    reactor.callLater(1, p.unsub, 1, 1)
    reactor.callLater(1.1, p.pub, "happy", "Hello world")
    reactor.callLater(2, p.transport.loseConnection)

host = "demo.nats.io"
port = 4222

point = TCP4ClientEndpoint(reactor, host, port)
d = connectProtocol(point, NatsClient())
d.addCallback(gotProtocol)
reactor.run()
