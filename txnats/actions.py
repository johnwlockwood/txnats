from __future__ import division, absolute_import

import attr
from .config_state import ServerInfo
from .validators import is_instance_of_nats_protocol


@attr.s
class ReceivedPing(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    

@attr.s
class ReceivedPong(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)


@attr.s
class ReceivedMsg(object):
    sid = attr.ib(validator=attr.validators.instance_of(int))
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    subject = attr.ib(default="")
    payload = attr.ib(default=None,
        validator=attr.validators.instance_of((bytes, str))
    )
    reply_to = attr.ib(default=None, 
        validator=attr.validators.optional(
            attr.validators.instance_of((bytes, str, unicode))
        )
    )


@attr.s
class ReceivedInfo(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    server_info = attr.ib(default=None, 
        validator=attr.validators.instance_of(ServerInfo))


@attr.s
class Unsub(object):
    sid = attr.ib(validator=attr.validators.instance_of(int))
    protocol = attr.ib(validator=is_instance_of_nats_protocol)


@attr.s
class ReceivedMsg(object):
    sid = attr.ib(validator=attr.validators.instance_of(int))
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    subject = attr.ib(default="")
    queue_group = attr.ib(default=None, 
        validator=attr.validators.optional(
            attr.validators.instance_of((bytes, str, unicode))
        )
    )
    on_msg = attr.ib(default=None)


@attr.s
class UnhandledCommand(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    command = attr.ib(default=None)


@attr.s
class ConnectionLost(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    reason = attr.ib(default=None)


@attr.s
class Disconnect(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    reason = attr.ib(default=None)


@attr.s
class Connect(object):
    protocol = attr.ib(validator=is_instance_of_nats_protocol)
    client_info = attr.ib(default=None)