from io import BytesIO

from twisted.trial import unittest
from twisted.internet import task
from twisted.internet import defer


import txnats


class ErrorTest(unittest.TestCase):
    maxDiff = None

    @defer.inlineCallbacks
    def setUp(self):
        """
        Create protocol.

        Add any fixtures.

        :return:
        """
        yield

    def test_on_connect_error(self):
        """
        Ensure an unhandled error in an on connect function is reported.
        """
        def on_connect(protocol):
            raise ValueError("It is wrong.")

        nats_protocol = txnats.io.NatsProtocol(own_reactor=task.Clock(), on_connect=on_connect)
        nats_protocol.on_connect_d.callback(nats_protocol)
        self.failureResultOf(nats_protocol.on_connect_d, ValueError)

    def tearDown(self):
        """
        Any tear down.

        :return:
        """
