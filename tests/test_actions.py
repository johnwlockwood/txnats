
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
        actions.ReceivedPong(txnats.io.NatsProtocol())

    def test_unsub(self):
        actions.Unsub("4", txnats.io.NatsProtocol())
