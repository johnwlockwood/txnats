
from twisted.trial import unittest

import txnats
from txnats import actions

class IsNatsProtocolTest(unittest.TestCase):
    maxDiff = None
    def test_received_ping(self):
        """
        Ensure ReceivedPing can be instanciated.
        """
        actions.ReceivedPing(protocol=txnats.io.NatsProtocol())

    def test_received_pong(self):
        """
        Ensure ReceivedPong takes the protocol.
        """
        actions.ReceivedPong(txnats.io.NatsProtocol(), outstanding_pings=0)    

    def test_send_ping(self):
        """
        Ensure SendPing takes the protocol.
        """
        actions.SendPing(txnats.io.NatsProtocol(), outstanding_pings=1)

    def test_sub_removed(self):
        actions.UnsubMaxReached("4", txnats.io.NatsProtocol())

    def test_send_unsub_immediate(self):
        "Ensure SendUnsub accepts no max_msgs"
        actions.SendUnsub("5", txnats.io.NatsProtocol())

    def test_send_unsub(self):
        actions.SendUnsub("5", txnats.io.NatsProtocol(), 3)
    
    def test_send_sub(self):
        actions.SendSub("6", txnats.io.NatsProtocol(), "a_subject")

    def test_send_pub(self):
        actions.SendPub(txnats.io.NatsProtocol(), "a_subject", b"hello", "callme")