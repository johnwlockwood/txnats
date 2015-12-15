from . import _meta


__version__ = _meta.version
__version_info__ = _meta.version_info

from . import txnats as io
from .txnats import NatsProtocol

__all__ = [
    'io',
    'NatsProtocol'
]
