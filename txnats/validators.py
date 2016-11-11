from __future__ import division, absolute_import

def is_instance_of_nats_protocol(instance, attribute, value):
    from .protocol import NatsProtocol
    if not isinstance(value, NatsProtocol):
        raise ValueError("The value of {} must be an instance of NatsProtocol!".format(attribute.name))
