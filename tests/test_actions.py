
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

    def test_request_unsub_immediate(self):
        "Ensure RequestUnsub accepts no max_msgs"
        actions.RequestUnsub("5", txnats.io.NatsProtocol())

    def test_request_unsub(self):
        actions.RequestUnsub("5", txnats.io.NatsProtocol(), 3)
