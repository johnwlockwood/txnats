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

