from __future__ import division, absolute_import

import attr

@attr.s(slots=True)
class SubscriptionArgs(object):
    subject = attr.ib(validator=attr.validators.instance_of((type(u""), type(""))))
    sid = attr.ib(validator=attr.validators.instance_of((type(u""), type(""))))
    queue_group = attr.ib(default=None)
    on_msg = attr.ib(default=None)


@attr.s(slots=True, frozen=True)
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


@attr.s(slots=True, frozen=True)
class ClientInfo(object):
    verbose = attr.ib(validator=attr.validators.instance_of(bool))
    pedantic = attr.ib(validator=attr.validators.instance_of(bool))
    ssl_required = attr.ib(validator=attr.validators.instance_of(bool))
    auth_token = attr.ib(default=None)
    user = attr.ib(default=None)
    password = attr.ib(default=None)
    name = attr.ib(default="txnats")
    lang = attr.ib(default="py.twisted")
    version = attr.ib(default="")

    def asdict_for_connect(self):
        client_info = attr.asdict(self, 
            filter=attr.filters.exclude(
                attr.fields(self.__class__).password))
        client_info["pass"] = self.password
        return client_info
