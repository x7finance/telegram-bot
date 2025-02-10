from .blockspan import Blockspan
from .coingecko import Coingecko
from .defined import Defined
from .dextools import Dextools
from .dune import Dune
from .etherscan import Etherscan
from .github import GitHub
from .mysql import MySql
from .opensea import Opensea
from .snapshot import Snapshot
from .twitter import Twitter

_cached_services = {}


def get_service(service_class):
    global _cached_services
    if service_class not in _cached_services:
        _cached_services[service_class] = service_class()
    return _cached_services[service_class]


_services = {
    "blockspan": Blockspan,
    "coingecko": Coingecko,
    "defined": Defined,
    "dextools": Dextools,
    "dune": Dune,
    "etherscan": Etherscan,
    "github": GitHub,
    "mysql": MySql,
    "opensea": Opensea,
    "snapshot": Snapshot,
    "twitter": Twitter,
}


def get_blockspan() -> Blockspan:
    return get_service(Blockspan)


def get_coingecko() -> Coingecko:
    return get_service(Coingecko)


def get_defined() -> Defined:
    return get_service(Defined)


def get_dextools() -> Dextools:
    return get_service(Dextools)


def get_dune() -> Dune:
    return get_service(Dune)


def get_etherscan() -> Etherscan:
    return get_service(Etherscan)


def get_github() -> GitHub:
    return get_service(GitHub)


def get_mysql() -> MySql:
    return get_service(MySql)


def get_opensea() -> Opensea:
    return get_service(Opensea)


def get_snapshot() -> Snapshot:
    return get_service(Snapshot)


def get_twitter() -> Twitter:
    return get_service(Twitter)


for service_name, service_class in _services.items():

    def make_getter(cls):
        def getter():
            return get_service(cls)

        return getter

    globals()[f"get_{service_name}"] = make_getter(service_class)


__all__ = list(_services.keys()) + [f"get_{name}" for name in _services.keys()]
