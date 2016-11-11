from . import _meta


__version__ = _meta.version
__version_info__ = _meta.version_info

from . import protocol as io
from .protocol import NatsProtocol
from .backoff import Backoff

__all__ = [
    'io',
    'NatsProtocol',
    'Backoff'
]
