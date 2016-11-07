from __future__ import division, absolute_import

import attr
from .config_state import ServerInfo
from .validators import is_instance_of_nats_protocol


@attr.s
class ReceivedPing(object):
    protocol = attr.ib(default=None, 
        validator=attr.validators.optional(
            is_instance_of_nats_protocol
        )
    )

@attr.s
class ReceivedPong(object):
    protocol = attr.ib(default=None, 
        validator=attr.validators.optional(
            is_instance_of_nats_protocol
        )
    )

@attr.s
class ReceivedMsg(object):
    protocol = attr.ib(default=None, 
        validator=attr.validators.optional(
            is_instance_of_nats_protocol
        )
    )

    sid = attr.ib(validator=attr.validators.instance_of(int))
    subject = attr.ib(default="")
    payload = attr.ib(
        validator=attr.validators.instance_of((bytes, str))
    )
    reply_to = attr.ib(default=None, 
        validator=attr.validators.optional(
            attr.validators.instance_of((bytes, str, unicode)))
        )
    )

@attr.s
class ReceivedInfo(object):
    protocol = attr.ib(default=None, 
        validator=attr.validators.optional(
            is_instance_of_nats_protocol
        )
    )
    server_info = attr.ib(default=None, 
        validator=attr.validators.instance_of(ServerInfo))
