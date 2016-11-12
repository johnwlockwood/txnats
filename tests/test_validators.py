import attr
from twisted.trial import unittest

import txnats
from txnats.validators import is_instance_of_nats_protocol
from txnats.validators import is_subject
from txnats.validators import is_subject_id


@attr.s
class Foo(object):
    subject = attr.ib(validator=is_subject)
    sid = attr.ib(validator=is_subject_id)
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
        Foo("A.*", "33", protocol=txnats.io.NatsProtocol())

    def test_wildcard_delimited_valid(self):
        Foo("A.*", "33", protocol=txnats.io.NatsProtocol())
        Foo("A.*.thing", "33", protocol=txnats.io.NatsProtocol())
        Foo("A.>", "33", protocol=txnats.io.NatsProtocol())
        Foo("A.*", "33", protocol=txnats.io.NatsProtocol())

    def test_wildcard_invalid(self):
        with self.assertRaises(ValueError):
            Foo("A.>ewr", "33", protocol=txnats.io.NatsProtocol())

        with self.assertRaises(ValueError):
            Foo("A>", "33", protocol=txnats.io.NatsProtocol())
        
        with self.assertRaises(ValueError):
            Foo("A*.la", "33", protocol=txnats.io.NatsProtocol())
        
        with self.assertRaises(ValueError):
            Foo("A.*la", "33", protocol=txnats.io.NatsProtocol())
    
    def test_foo_none(self):
        """
        Ensure Foo.protocol may be None.
        """
        Foo("B.2.>", "33")

    def test_foo_invalid(self):
        """
        Ensure any other value is invalid for Foo.protocol.
        """
        with self.assertRaises(ValueError):
            Foo("C3", "33", protocol=4)

    def test_foo_subject_not_alnum(self):
        """
        Ensure a subject not composed of strictly alphanumeric chars is
        invalid.
        """
        with self.assertRaises(ValueError):
            Foo("C 3", "33")

    def test_foo_subject_not_empty(self):
        """
        Ensure an empty string subject is not valid.
        """
        with self.assertRaises(ValueError):
            Foo("", "33")

