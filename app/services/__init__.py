import inspect
import sys

from .codex import Codex
from .coingecko import Coingecko
from .dextools import Dextools
from .db import db
from .dune import Dune
from .etherscan import Etherscan
from .github import GitHub
from .snapshot import Snapshot
from .twitter import Twitter

_cached_services = {}


def get_service(service_class):
    global _cached_services
    if service_class not in _cached_services:
        _cached_services[service_class] = service_class()
    return _cached_services[service_class]


def get_codex() -> Codex:
    return get_service(Codex)


def get_coingecko() -> Coingecko:
    return get_service(Coingecko)


def get_dextools() -> Dextools:
    return get_service(Dextools)


def get_dbmanager():
    return db


def get_dune() -> Dune:
    return get_service(Dune)


def get_etherscan() -> Etherscan:
    return get_service(Etherscan)


def get_github() -> GitHub:
    return get_service(GitHub)


def get_snapshot() -> Snapshot:
    return get_service(Snapshot)


def get_twitter() -> Twitter:
    return get_service(Twitter)


def make_getter(cls):
    def getter():
        return get_service(cls)

    return getter


_current_module = sys.modules[__name__]

for name, cls in inspect.getmembers(_current_module, inspect.isclass):
    if cls.__module__ == __name__:
        function_name = f"get_{name.lower()}"
        globals()[function_name] = make_getter(cls)

__all__ = [
    f"get_{name.lower()}"
    for name, cls in inspect.getmembers(_current_module, inspect.isclass)
]
