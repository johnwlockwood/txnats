import attr
from twisted.trial import unittest

import txnats
from txnats.validators import is_instance_of_nats_protocol


@attr.s
class Foo(object):
    protocol = attr.ib(default=None, 
        validator=attr.validators.optional(
            is_instance_of_nats_protocol
        )
    )


class IsNatsProtocolTest(unittest.TestCase):
    maxDiff = None
    def test_foo_valid(self):
        """
        Ensure Foo.protocol may be a NatsProtocol.
        """
        Foo(protocol=txnats.io.NatsProtocol())
    
    def test_foo_none(self):
        """
        Ensure Foo.protocol may be None.
        """
        Foo()

    def test_foo_invalid(self):
        """
        Ensure any other value is invalid for Foo.protocol.
        """
        with self.assertRaises(ValueError):
            Foo(protocol=4)

