from sys import stdout
import logging
import json
from io import BytesIO
from io import BufferedReader
from collections import namedtuple

from twisted.python import log

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import Protocol


VERSION = "0.2.0"
LANG = "py.twisted"
CLIENT_NAME = "xnats"


ServerInfo = namedtuple(
    "ServerInfo",
    (
        "server_id",
        "version",
        "go",
        "host",
        "port",
        "auth_required",
        "ssl_required",
        "tls_required",
        "tls_verify",
        "max_payload",
    ))


DISCONNECTED = 0
CONNECTED = 1


class NatsError(Exception):
    "Nats Error"


class NatsProtocol(Protocol):
    server_settings = None

    def __init__(self, own_reactor=None, verbose=True, pedantic=False,
                 ssl_required=False, auth_token=None, user="",
                 password="", on_msg=None):
        """

        @param verbose: Turns on +OK protocol acknowledgements.
        @param pedantic: Turns on additional strict format checking, e.g.
         for properly formed subjects
        @param ssl_required: Indicates whether the client requires
         an SSL connection.
        @param auth_token: Client authorization token
        @param user: Connection username (if auth_required is set)
        @param pass: Connection password (if auth_required is set)
        """
        self.reactor = own_reactor if own_reactor else reactor
        self.status = DISCONNECTED
        self.verbose = verbose
        # Set the number of PING sent out
        self.pout = 0

        self.client_info = {
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
        self.on_msg = on_msg
        self.on_connect_d = defer.Deferred()
        self.sids = {}

    def dataReceived(self, data):
        data_buf = BufferedReader(BytesIO(data))
        while True:
            command = data_buf.read(4)
            if command == "-ERR":
                self.status = DISCONNECTED
                raise NatsError(data_buf.read())
            elif command == "+OK\r":
                data_buf.read(1)
            elif command == "MSG ":
                meta_data = data_buf.readline().split(" ")
                n_bytes = int(meta_data[-1])
                subject = meta_data[0]
                if len(meta_data) == 4:
                    reply_to = meta_data[2]
                else:
                    reply_to = None
                sid = int(meta_data[1])
                if sid in self.sids:
                    on_msg = self.sids[sid]
                else:
                    on_msg = None

                if on_msg:
                    on_msg(self, sid, subject, reply_to,
                           data_buf.read(n_bytes))
                    data_buf.readline()
                elif self.on_msg:
                    self.on_msg(self, data_buf.read(n_bytes))
                    data_buf.readline()
                else:
                    stdout.write(data_buf.read(n_bytes))
                    stdout.write(data_buf.readline())
            elif command == "PING":
                self.pong()
                data_buf.readline()
            elif command == "PONG":
                self.pout -= 1
                data_buf.readline()
            elif command == "INFO":
                settings = json.loads(data_buf.read())
                self.server_settings = ServerInfo(**settings)
                self.status = CONNECTED
                self.connect()
                self.on_connect_d.callback(self)
            else:
                log.msg("Not handled command is: {!r}".format(command),
                        logLevel=logging.DEBUG)
            if not data_buf.peek(1):
                log.msg("emptied data",
                        logLevel=logging.DEBUG)
                break

    def connect(self):
        """
        Tell the NATS server about this client and it's options.
        """
        payload = b'CONNECT {}\r\n'.format(json.dumps(
            self.client_info, separators=(',', ':')))

        log.msg(payload, logLevel=logging.DEBUG)
        self.transport.write(payload)

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

        # TODO: deal with the payload if it is bigger than the server max.
        op = b"PUB {} {}{}\r\n{}\r\n".format(
            subject, reply_part, len(payload), payload)
        self.transport.write(op)

    def sub(self, subject, sid, queue_group=None, on_msg=None):
        """
        Subscribe to a subject.

        @param subject: The subject name to subscribe to.
        @param sid: A unique alphanumeric subscription ID.
        @param queue_group: If specified, the subscriber will
         join this queue group.
        """
        self.sids[sid] = on_msg

        queue_group_part = b""
        if queue_group:
            queue_group_part = b"{} ".format(queue_group)

        op = b"SUB {} {}{}\r\n".format(subject, sid, queue_group_part)
        self.transport.write(op)

    def unsub(self, sid, max_msgs=None):
        """
        Unsubcribes the connection from the specified subject,
        or auto-unsubscribes after the specified
        number of messages has been received.

        @param sid: The unique alphanumeric subscription ID of
         the subject to unsubscribe from.
        @type sid: int
        @param max_msgs: Optional number of messages to wait for before
         automatically unsubscribing.
        @type sid: int
        """
        max_msgs_part = b""
        if max_msgs:
            max_msgs_part = b"{}".format(max_msgs)

        op = b"UNSUB {} {}\r\n".format(sid, max_msgs_part)
        self.transport.write(op)

    def ping(self):
        """
        Send ping.
        """
        op = b"PING\r\n"
        self.transport.write(op)
        self.pout += 1

    def pong(self):
        """
        Send pong.
        """
        op = b"PONG\r\n"
        self.transport.write(op)

