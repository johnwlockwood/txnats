from __future__ import division, absolute_import

import attr

@attr.s
class SubscriptionArgs(object):
    subject = attr.ib(default=None)
    sid = attr.ib(default=None)
    queue_group = attr.ib(default=None)
    on_msg = attr.ib(default=None)


@attr.s
class ServerInfo(object):
    server_id = attr.ib(default=None)
    version = attr.ib(default=None)
    go = attr.ib(default=None)
    host = attr.ib(default=None)
    port = attr.ib(default=None)
    auth_required = attr.ib(default=None)
    ssl_required = attr.ib(default=None)
    tls_required = attr.ib(default=None)
    tls_verify = attr.ib(default=None)
    max_payload = attr.ib(default=None)
