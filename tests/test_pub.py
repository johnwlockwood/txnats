from tests.base import BaseTest


class TestPub(BaseTest):
    def test_pub_with_reply_to(self):
        """
        Ensure pub sends the protocol PUB message with the reply_to
        subject included.
        """
        def msg_handler(*args, **kwargs):
            pass
        self.nats_protocol.pub("a-queue", "Do something!", 'inbox')
        self.assertEqual(self.transport.getvalue(),
                         b"PUB a-queue inbox 13\r\nDo something!\r\n")
