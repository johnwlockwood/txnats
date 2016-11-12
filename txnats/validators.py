import re

SID_SUBJECT_TYPES = (type(u""), type(""))


def is_instance_of_nats_protocol(instance, attribute, value):
    from .protocol import NatsProtocol
    if not isinstance(value, NatsProtocol):
        raise ValueError(
            "The value of {} must be an instance of NatsProtocol!".format(
                attribute.name))


def is_subject_id(instance, attribute, value):
    if not isinstance(value, SID_SUBJECT_TYPES) or not value.isalnum():
        raise ValueError(
            "The value of {} must be an alpha numeric string! got: '{}''".format(
                attribute.name, value))


def is_subject(instance, attribute, value):
    if not isinstance(value, SID_SUBJECT_TYPES) or not re.match("^[\w\d\.\*\>]+$", value):
        raise ValueError(
            "The value of {} must be an alpha numeric string with the "
            "exception of '*' '.' and '>'! got: {}".format(
                attribute.name, value))
