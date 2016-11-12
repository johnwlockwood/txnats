from __future__ import division, absolute_import
from sys import stdout
import attr
import json
from io import BytesIO
from io import BufferedReader
from collections import namedtuple

from twisted.logger import Logger

from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import connectionDone
from twisted.internet import error

from . import _meta
from .config_state import ServerInfo
from .config_state import ClientInfo
from .config_state import SubscriptionArgs
from . import actions
from .errors import NatsError


LANG = "py.twisted"
CLIENT_NAME = "txnats"

DISCONNECTED = 0
CONNECTED = 1


class NatsProtocol(Protocol):
    server_settings = None
    log = Logger()

    def __init__(self, own_reactor=None, verbose=True, pedantic=False,
                 ssl_required=False, auth_token=None, user="",
                 password="", on_msg=None, on_connect=None, 
                 event_subscribers=None, subscriptions=None, unsubs=None):
        """

        @param own_reactor: A Twisted Reactor, defaults to standard. Chiefly
         customizable for testing.
        @param verbose: Turns on +OK protocol acknowledgements.
        @param pedantic: Turns on additional strict format checking, e.g.
         for properly formed subjects
        @param ssl_required: Indicates whether the client requires
         an SSL connection.
        @param auth_token: Client authorization token
        @param user: Connection username (if auth_required is set)
        @param pass: Connection password (if auth_required is set)
        @param on_msg: Handler for messages for subscriptions that don't have
         their own on_msg handler. Default behavior is to write to stdout.
         A callable that takes the following params:
             @param nats_protocol: An instance of NatsProtocol.
             @param sid: A unique alphanumeric subscription ID.
             @param subject: A valid NATS subject.
             @param reply_to: The reply to.
             @param payload: Bytes of the payload.
        @param on_connect: Callable that takes this instance of NatsProtocol
         which will be called upon the first successful connection.
        @param event_subscribers: A collection of functions that take an 
         event/action entity.
        @param subscriptions: A dict of sids and SubscriptionArgs.
        @param unsubs: A dict of sids and ints representing the number 
         of messages for the sid before automatic unsubscription.
        """
        self.reactor = own_reactor if own_reactor else reactor
        self.status = DISCONNECTED
        self.verbose = verbose
        # Set the number of PING sent out
        self.ping_loop = LoopingCall(self.ping)
        self.pout = 0
        self.remaining_bytes = b''

        self.client_info = ClientInfo(
            verbose, pedantic, ssl_required, 
            auth_token, user, password, 
            CLIENT_NAME, LANG, _meta.version)

        if on_msg:
            # Ensure the on_msg signature fits.
            on_msg(nats_protocol=self, sid="0", subject="testSubject",
                   reply_to='inBox', payload=b'hello, world')
        self.on_msg = on_msg
        self.on_connect = on_connect
        self.on_connect_d = defer.Deferred()
        if on_connect:
            self.on_connect_d.addCallback(on_connect)
        self.sids = {}
        self.subscriptions = subscriptions if subscriptions is not None else {}
        self.unsubs = unsubs if unsubs else {}
        self.event_subscribers = event_subscribers if event_subscribers is not None else []
    
    def __repr__(self):
        return r'<NatsProtocol connected={} server_info={}>'.format(self.status, self.server_settings)

    def dispatch(self, event):
        """Call each event subscriber with the event.
        """
        if self.event_subscribers is None:
            return
        for event_subscriber in self.event_subscribers:
            event_subscriber(event)
        return

    def connectionLost(self, reason=connectionDone):
        """Called when the connection is shut down.

        Clear any circular references here, and any external references
        to this Protocol.  The connection has been closed.

        Clear left over remaining bytes because they won't be continued
        properly upon reconnection.

        @type reason: L{twisted.python.failure.Failure}
        """
        self.status = DISCONNECTED
        self.remaining_bytes = b''
        if reason.check(error.ConnectionLost):
            self.dispatch(actions.ConnectionLost(self, reason=reason))
        else:  
            self.dispatch(actions.Disconnected(self, reason=reason))

    def dataReceived(self, data):
        """
        Parse the NATS.io protocol from chunks of data streaming from
        the connected gnatsd.

        The server settings will be set and connect will be sent with this
        client's info upon an INFO, which should happen when the
        transport connects.

        Registered message callback functions will be called with MSGs
        once parsed.

        PONG will be called upon a ping.

        An exception will be raised upon an ERR from gnatsd.

        An +OK doesn't do anything.
        """
        if self.remaining_bytes:
            data = self.remaining_bytes + data
            self.remaining_bytes = b''

        data_buf = BufferedReader(BytesIO(data))
        while True:
            command = data_buf.read(4)
            if command == b"-ERR":
                raise NatsError(data_buf.read())
            elif command == b"+OK\r":
                val = data_buf.read(1)
                if val != b'\n':
                    self.remaining_bytes += command
                    break
            elif command == b"MSG ":
                val = data_buf.readline()
                if not val:
                    self.remaining_bytes += command
                    break
                if not val.endswith(b'\r\n'):
                    self.remaining_bytes += command + val
                    break

                meta_data = val.split(b" ")
                n_bytes = int(meta_data[-1])
                subject = meta_data[0].decode()
                if len(meta_data) == 4:
                    reply_to = meta_data[2].decode()
                elif len(meta_data) == 3:
                    reply_to = None
                else:
                    self.remaining_bytes += command + val
                    break

                sid = meta_data[1].decode()

                if sid in self.sids:
                    on_msg = self.sids[sid]
                else:
                    on_msg = self.on_msg

                payload = data_buf.read(n_bytes)
                if len(payload) != n_bytes:
                    self.remaining_bytes += command + val + payload
                    break

                if on_msg:
                    on_msg(nats_protocol=self, sid=sid, subject=subject,
                           reply_to=reply_to, payload=payload)
                else:
                    stdout.write(command.decode())
                    stdout.write(val.decode())
                    stdout.write(payload.decode())

                self.dispatch(
                    actions.ReceivedMsg(
                        sid, self, 
                        subject=subject, 
                        payload=payload, 
                        reply_to=reply_to)
                    )

                if sid in self.unsubs:
                    self.unsubs[sid] -= 1
                    if self.unsubs[sid] <= 0:
                        self._forget_subscription(sid)
                        self.dispatch(actions.UnsubMaxReached(sid, protocol=self))

                payload_post = data_buf.readline()
                if payload_post != b'\r\n':
                    self.remaining_bytes += (command + val + payload
                                             + payload_post)
                    break
            elif command == b"PING":
                self.dispatch(actions.ReceivedPing(self))
                self.pong()
                val = data_buf.readline()
                if val != b'\r\n':
                    self.remaining_bytes += command + val
                    break
            elif command == b"PONG":
                self.pout -= 1
                self.dispatch(actions.ReceivedPong(self, outstanding_pings=self.pout))
                val = data_buf.readline()
                if val != b'\r\n':
                    self.remaining_bytes += command + val
                    break
            elif command == b"INFO":
                val = data_buf.readline()
                if not val.endswith(b'\r\n'):
                    self.remaining_bytes += command + val
                    break
                settings = json.loads(val.decode('utf8'))
                self.server_settings = ServerInfo(**settings)
                self.dispatch(actions.ReceivedInfo(
                    self, server_info=self.server_settings))
                self.status = CONNECTED
                self.pout = 0
                self.sids = {}
                self.connect()
                if self.on_connect_d:
                    self.on_connect_d.callback(self)
                    self.on_connect_d = None
            else:
                self.dispatch(actions.UnhandledCommand(self, command=command))
                val = data_buf.read()
                self.remaining_bytes += command + val
            if not data_buf.peek(1):
                break

    def connect(self):
        """
        Tell the NATS server about this client and it's options.
        """
        payload = 'CONNECT {}\r\n'.format(json.dumps(
            self.client_info.asdict_for_connect()
            , separators=(',', ':')))

        self.transport.write(payload.encode())
        self.dispatch(actions.SendConnect(self, client_info=self.client_info))

    def pub(self, subject,  payload, reply_to=None):
        """
        Publish a payload of bytes to a subject.

        @param subject: The destination subject to publish to.
        @param reply_to: The reply inbox subject that subscribers can use
         to send a response back to the publisher/requestor.
        @param payload: The message payload data, in bytes.
        """
        action = actions.SendPub(self, subject,  payload, reply_to)
        reply_part = ""
        if reply_to:
            reply_part = "{} ".format(reply_to)

        # TODO: deal with the payload if it is bigger than the server max.
        op = "PUB {} {}{}\r\n".format(
            subject, reply_part, len(payload)).encode()
        op += payload + b'\r\n'
        self.transport.write(op)
        self.dispatch(action)

    def apply_subscriptions(self):
        """
        Subscribe all the subscriptions and unsubscribe all of 
        the unsubscriptions.

        Builds the state of subscriptions and unsubscriptions 
        with max messages.
        """
        if self.status == CONNECTED:
            for sid, sub_args in self.subscriptions.items():
                self.sub(
                    sub_args.subject, sub_args.sid, 
                    sub_args.queue_group, sub_args.on_msg)
                if sid in self.unsubs:
                    self.unsub(sid, max_msgs=self.unsubs[sid])

    def sub(self, subject, sid, queue_group=None, on_msg=None):
        """
        Subscribe to a subject.

        @param subject: The subject name to subscribe to.
        @param sid: A unique alphanumeric subscription ID.
        @param queue_group: If specified, the subscriber will
         join this queue group.
         @param on_msg: A callable that takes the following params:
             @param nats_protocol: An instance of NatsProtocol.
             @param sid: A unique alphanumeric subscription ID.
             @param subject: A valid NATS subject.
             @param reply_to: The reply to.
             @param payload: Bytes of the payload.
        """
        self.sids[sid] = on_msg
        self.subscriptions[sid] = SubscriptionArgs(
            subject, sid, queue_group, on_msg)
        self.dispatch(actions.SendSub(
            sid=sid,
            protocol=self,
            subject=subject,
            queue_group=queue_group,
            on_msg=on_msg
        ))

        queue_group_part = ""
        if queue_group:
            queue_group_part = "{} ".format(queue_group)

        op = "SUB {} {}{}\r\n".format(subject, queue_group_part, sid)
        self.transport.write(op.encode('utf8'))

    def _forget_subscription(self, sid):
        """Undeclare a subscription. Any on_msg declared for the subscription 
        will no longer be called.
        If a apply_subscriptions is called,
        which it is during a reconnect, These subscriptions will not be 
        established. """
        if sid in self.unsubs:
            del self.unsubs[sid]
        if sid in self.subscriptions:
            del self.subscriptions[sid]
        if sid in self.sids:
            del self.sids[sid]

    def unsub(self, sid, max_msgs=None):
        """
        Unsubcribes the connection from the specified subject,
        or auto-unsubscribes after the specified
        number of messages has been received.

        @param sid: The unique alphanumeric subscription ID of
         the subject to unsubscribe from.
        @type sid: str
        @param max_msgs: Optional number of messages to wait for before
         automatically unsubscribing.
        @type max_msgs: int
        """
        max_msgs_part = ""
        if max_msgs:
            max_msgs_part = "{}".format(max_msgs)
            self.unsubs[sid] = max_msgs
        else:
            self._forget_subscription(sid)

        op = "UNSUB {} {}\r\n".format(sid, max_msgs_part)
        self.transport.write(op.encode('utf8'))
        self.dispatch(actions.SendUnsub(sid=sid, protocol=self, max_msgs=max_msgs))

    def ping(self):
        """
        Send ping.
        """
        op = b"PING\r\n"
        self.transport.write(op)
        self.pout += 1
        self.dispatch(actions.SendPing(self, outstanding_pings=self.pout))

    def pong(self):
        """
        Send pong.
        """
        op = b"PONG\r\n"
        self.transport.write(op)
        self.dispatch(actions.SendPong(self))

    def request(self, sid, subject):
        """
        Make a synchronous request for a subject.

        Make a reply to.
        Subscribe to the subject.
        Make a Deferred and add it to the inbox under the reply to.
        Do auto unsubscribe for one message.
        """
        raise NotImplementedError()
