from mock import patch
from mock import Mock

import json

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
        yield

    def tearDown(self):
        """
        Any tear down.

        :return:
        """


class TestDataReceived(BaseTest):
    def test_split_msg_payload(self):
        """
        Ensure a MSG command split across dataReceived within the payload is
        still processed the same, even if the payload ends with newline bytes.
        """
        with patch("txnats.io.NatsProtocol.transport") as mock_transport:
            mock_msg_handler = Mock()
            self.nats_protocol.sub('inbox', 1, on_msg=mock_msg_handler)
            mock_transport.write.assert_called_once_with("SUB inbox 1\r\n")
            self.nats_protocol.dataReceived(
                "MSG mysubject 1 inbox1 7\r\nh\r\n"
            )
            self.nats_protocol.dataReceived(
                "ello\r\n"
            )
            mock_msg_handler.assert_called_once_with(
                self.nats_protocol, 1, 'mysubject', 'inbox1', 'h\r\nello')

    def test_split_msg_with_partial_fake_msg_in_payload(self):
        """
        Ensure a MSG command split across dataReceived within the payload is
        still processed the same, even if the payload ends with newline bytes
        contains bytes that match the beginning of another command.
        """
        with patch("txnats.io.NatsProtocol.transport") as mock_transport:
            mock_msg_handler = Mock()
            self.nats_protocol.sub('inbox', 1, on_msg=mock_msg_handler)
            mock_transport.write.assert_called_once_with("SUB inbox 1\r\n")
            self.nats_protocol.dataReceived(
                "MSG mysubject 1 inbox1 41\r\nh\r\n"
            )
            self.nats_protocol.dataReceived(
                "ello\r\nMSG asubject 3 breply 6\r\nsausage\r\n"
            )
            mock_msg_handler.assert_called_once_with(
                self.nats_protocol, 1, 'mysubject', 'inbox1',
                "h\r\nello\r\nMSG asubject 3 breply 6\r\nsausage")

    def test_split_msg_command(self):
        """
        Ensure a MSG command split within the first few bytes is handled.
        """
        with patch("txnats.io.NatsProtocol.transport") as mock_transport:
            mock_msg_handler = Mock()
            self.nats_protocol.sub('inbox', 1, on_msg=mock_msg_handler)
            mock_transport.write.assert_called_once_with("SUB inbox 1\r\n")
            self.nats_protocol.dataReceived(
                "MS"
            )
            self.nats_protocol.dataReceived(
                "G mysubject 1 inbox1 7\r\nh\r\nello\r\n"
            )
            mock_msg_handler.assert_called_once_with(
                self.nats_protocol, 1, 'mysubject', 'inbox1', 'h\r\nello')

    def test_split_stream(self):
        """
        Ensure a command split across multiple dataReceived calls is parsed
        and handled the same as commands wholely within one dataReceived.

        Ensure the next data received after one in where there was a previous
        protocol split is processed normally.
        """
        with patch("txnats.io.NatsProtocol.transport") as mock_transport:
            self.nats_protocol.dataReceived(
                "PI"
            )
            self.nats_protocol.dataReceived(
                "NG\r\n"
            )
            mock_transport.write.assert_called_once_with(
                'PONG\r\n'
            )
            self.nats_protocol.dataReceived(
                "PING\r\n"
            )
            mock_transport.write.assert_called_with(
                'PONG\r\n'
            )
            self.assertEqual(mock_transport.write.call_count, 2)

    @defer.inlineCallbacks
    def test_info(self):
        """
        Ensure upon receiving an INFO operation, the server info is
        parsed and saved and a CONNECT operation is sent.

        """
        with patch("txnats.io.NatsProtocol.transport") as mock_transport:
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

            mock_transport.write.assert_called_once_with(
                'CONNECT {"lang":"py.twisted","pedantic":false,'
                '"version":"' + txnats.__version__ + '","verbose":true,'
                '"name":"xnats",'
                '"pass":"","auth_token":null,'
                '"ssl_required":false,"user":""}\r\n'
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
