from __future__ import division, absolute_import

import attr
from .config_state import ServerInfo
from .validators import is_instance_of_nats_protocol


SID_TYPES = (type(u""), type(""))


@attr.s(slots=True)
class SendPing(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    outstanding_pings = attr.ib(validator=attr.validators.instance_of(int))

@attr.s(slots=True)
class ReceivedPing(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    

@attr.s(slots=True)
class SendPong(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)


@attr.s(slots=True)
class ReceivedPong(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    outstanding_pings = attr.ib(validator=attr.validators.instance_of(int))


@attr.s(slots=True)
class ReceivedMsg(object):
    sid = attr.ib(validator=attr.validators.instance_of(SID_TYPES))
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    subject = attr.ib(validator=attr.validators.instance_of(SID_TYPES))
    payload = attr.ib(validator=attr.validators.instance_of(bytes))
    reply_to = attr.ib( 
        validator=attr.validators.optional(
            attr.validators.instance_of(SID_TYPES)
        )
    )


@attr.s(slots=True)
class ReceivedInfo(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    server_info = attr.ib(validator=attr.validators.instance_of(ServerInfo))


@attr.s(slots=True)
class UnsubMaxReached(object):
    sid = attr.ib(validator=attr.validators.instance_of(SID_TYPES))
    protocol = attr.ib(validator=is_instance_of_nats_protocol)


@attr.s(slots=True)
class SendUnsub(object):
    sid = attr.ib(validator=attr.validators.instance_of(SID_TYPES))
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    max_msgs = attr.ib(
        default=None, 
        validator=attr.validators.optional(attr.validators.instance_of(int)))


@attr.s(slots=True)
class SendSub(object):
    """Request a subscription"""
    sid = attr.ib(validator=attr.validators.instance_of(SID_TYPES))
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    subject = attr.ib(validator=attr.validators.instance_of(SID_TYPES))
    queue_group = attr.ib(default=None, 
        validator=attr.validators.optional(
            attr.validators.instance_of(SID_TYPES)
        )
    )
    on_msg = attr.ib(default=None)


@attr.s(slots=True)    
class SendPub(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    subject = attr.ib(validator=attr.validators.instance_of(SID_TYPES))
    payload = attr.ib(validator=attr.validators.instance_of(bytes))
    reply_to = attr.ib(attr.validators.instance_of(SID_TYPES))


@attr.s(slots=True)
class UnhandledCommand(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    command = attr.ib(default=None)


@attr.s(slots=True)
class ConnectionLost(object):
    "Lost connection"
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    reason = attr.ib(default=None)


@attr.s(slots=True)
class Disconnected(object):
    "Got disconnected"
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    reason = attr.ib(default=None)


@attr.s(slots=True)
class SendConnect(object):
    """Sent CONNECT"""
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    client_info = attr.ib(default=None)
