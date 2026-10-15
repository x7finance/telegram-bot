__all__ = [
    "get_service",
    "get_codex",
    "get_coingecko",
    "get_dbmanager",
    "get_dextools",
    "get_dune",
    "get_etherscan",
    "get_github",
    "get_snapshot",
    "get_twitter",
]

_cached_services = {}


def get_service(service_class):
    if service_class not in _cached_services:
        _cached_services[service_class] = service_class()
    return _cached_services[service_class]


def get_codex():
    from .codex import Codex

    return get_service(Codex)


def get_coingecko():
    from .coingecko import Coingecko

    return get_service(Coingecko)


def get_dextools():
    from .dextools import Dextools

    return get_service(Dextools)


def get_dbmanager():
    from .db import db

    return db


def get_dune():
    from .dune import Dune

    return get_service(Dune)


def get_etherscan():
    from .etherscan import Etherscan

    return get_service(Etherscan)


def get_github():
    from .github import GitHub

    return get_service(GitHub)


def get_snapshot():
    from .snapshot import Snapshot

    return get_service(Snapshot)


def get_twitter():
    from .twitter import Twitter

    return get_service(Twitter)
