from tests.base import BaseTest


class TestPub(BaseTest):
    def test_pub(self):
        """
        Ensure pub sends the protocol PUB message with the given subject
        and payload.
        """
        def msg_handler(*args, **kwargs):
            pass
        self.nats_protocol.pub("aQueue", b"Do something!")
        self.assertEqual(self.transport.getvalue(),
                         b"PUB aQueue 13\r\nDo something!\r\n")

    def test_pub_with_reply_to(self):
        """
        Ensure pub sends the protocol PUB message with the reply_to
        subject included.
        """
        def msg_handler(*args, **kwargs):
            pass
        self.nats_protocol.pub("aQueue", b"Do something!", 'inbox')
        self.assertEqual(self.transport.getvalue(),
                         b"PUB aQueue inbox 13\r\nDo something!\r\n")
