import json
from io import BytesIO

from twisted.trial import unittest
from twisted.internet import task
from twisted.internet import defer

import txnats


class BaseTest(unittest.TestCase):
    maxDiff = None

    @defer.inlineCallbacks
    def setUp(self):
        """
        Create protocol.

        Add any fixtures.

        :return:
        """
        self.reactor = task.Clock()
        self.nats_protocol = txnats.io.NatsProtocol(
            own_reactor=self.reactor)
        self.nats_protocol.transport = BytesIO()
        self.transport = self.nats_protocol.transport
        yield

    def tearDown(self):
        """
        Any tear down.

        :return:
        """


class TestDataReceived(BaseTest):
    def test_queue_group_subscribe(self):
        """
        Ensure a given queue group is put in between the subject and
        subscription id in the SUB command.
        """
        def msg_handler(*args, **kwargs):
            pass
        self.nats_protocol.sub('inbox', "1",
                               queue_group="a-queue-group",
                               on_msg=msg_handler)
        self.assertEqual(self.transport.getvalue(),
                         b"SUB inbox a-queue-group 1\r\n")

    def test_split_msg_payload(self):
        """
        Ensure a MSG command split across dataReceived within the payload is
        still processed the same, even if the payload ends with newline bytes.
        """
        self.msg_handler_called = False

        def msg_handler(nats_protocol=None, sid=None,
                        subject=None, reply_to=None, payload=None):
            self.msg_handler_called = True
            self.assertEqual(nats_protocol, self.nats_protocol)
            self.assertEqual(sid, b"1")
            self.assertEqual(subject, b"mysubject")
            self.assertEqual(reply_to, b"inbox1")
            self.assertEqual(payload, b'h\r\nello')

        self.nats_protocol.sub('inbox', 1, on_msg=msg_handler)
        self.assertEqual(self.transport.getvalue(), b"SUB inbox 1\r\n")
        self.nats_protocol.dataReceived(
            "MSG mysubject 1 inbox1 7\r\nh\r\n"
        )
        self.nats_protocol.dataReceived(
            "ello\r\n"
        )
        self.assertTrue(self.msg_handler_called)

    def test_split_msg_with_partial_fake_msg_in_payload(self):
        """
        Ensure a MSG command split across dataReceived within the payload is
        still processed the same, even if the payload ends with newline bytes
        contains bytes that match the beginning of another command.
        """
        self.msg_handler_called = False
        def msg_handler(nats_protocol=None, sid=None,
                        subject=None, reply_to=None, payload=None):
            self.msg_handler_called = True
            self.assertEqual(nats_protocol, self.nats_protocol)
            self.assertEqual(sid, b"1")
            self.assertEqual(subject, b"mysubject")
            self.assertEqual(reply_to, b"inbox1")
            self.assertEqual(
                payload, b"h\r\nello\r\nMSG asubject 3 breply 6\r\nsausage")

        self.nats_protocol.sub('inbox', 1, on_msg=msg_handler)
        self.assertEqual(self.transport.getvalue(), b"SUB inbox 1\r\n")
        self.nats_protocol.dataReceived(
            b"MSG mysubject 1 inbox1 41\r\nh\r\n"
        )
        self.nats_protocol.dataReceived(
            "ello\r\nMSG asubject 3 breply 6\r\nsausage\r\n"
        )
        self.assertTrue(self.msg_handler_called)

    def test_split_msg_command(self):
        """
        Ensure a MSG command split within the first few bytes is handled.
        """
        self.msg_handler_called = False
        def msg_handler(nats_protocol=None, sid=None,
                        subject=None, reply_to=None, payload=None):
            self.msg_handler_called = True
            self.assertEqual(nats_protocol, self.nats_protocol)
            self.assertEqual(sid, b"1")
            self.assertEqual(subject, b"mysubject")
            self.assertEqual(reply_to, b"inbox1")
            self.assertEqual(payload, b'h\r\nello')

        self.nats_protocol.sub('inbox', 1, on_msg=msg_handler)
        self.assertEqual(self.transport.getvalue(), b"SUB inbox 1\r\n")
        self.nats_protocol.dataReceived(
            b"MS"
        )
        self.nats_protocol.dataReceived(
            b"G mysubject 1 inbox1 7\r\nh\r\nello\r\n"
        )
        self.assertTrue(self.msg_handler_called)

    def test_split_stream(self):
        """
        Ensure a command split across multiple dataReceived calls is parsed
        and handled the same as commands wholely within one dataReceived.

        Ensure the next data received after one in where there was a previous
        protocol split is processed normally.
        """
        self.nats_protocol.dataReceived(
            "PI"
        )
        self.nats_protocol.dataReceived(
            "NG\r\n"
        )
        self.assertEqual(self.transport.getvalue(), b"PONG\r\n")
        self.nats_protocol.dataReceived(
            "PING\r\n"
        )
        self.assertEqual(self.transport.getvalue(), b"PONG\r\nPONG\r\n")

    @defer.inlineCallbacks
    def test_info(self):
        """
        Ensure upon receiving an INFO operation, the server info is
        parsed and saved and a CONNECT operation is sent.

        """
        self.nats_protocol.dataReceived(
            "INFO {}\r\n".format(
                json.dumps(
                    {u'auth_required': False,
                        u'go': u'go1.5.2',
                        u'host': u'0.0.0.0',
                        u'max_payload': 1048576,
                        u'port': 4222,
                        u'server_id': u'16dd1049f122d8d3d148894074423d48',
                        u'ssl_required': False,
                        u'tls_required': False,
                        u'tls_verify': False,
                        u'version': u'0.7.2'}
                )
            )
        )
        command = self.transport.getvalue()[:8]
        self.assertEqual(command, b'CONNECT ')
        client_info = json.loads(self.transport.getvalue()[8:])
        self.assertEqual(
            client_info,
            {
                "verbose": True,
                "pedantic": False,
                "ssl_required": False,
                "auth_token": None,
                "user": "",
                "pass": "",
                "name": "txnats",
                "lang": "py.twisted",
                "version": txnats.__version__,
            }
        )

        self.assertEqual(
            self.nats_protocol.server_settings,
            txnats.io.ServerInfo(
                auth_required=False,
                go=u'go1.5.2',
                host=u'0.0.0.0',
                max_payload=1048576,
                port=4222,
                server_id=u'16dd1049f122d8d3d148894074423d48',
                ssl_required=False,
                tls_required=False,
                tls_verify=False,
                version=u'0.7.2'
            ))
        yield
