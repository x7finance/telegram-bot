# CHAINS

import os
from constants import ca, urls
import media

from web3 import Web3


class ChainInfo:
    def __init__(
        self,
        live: bool,
        trading: bool,
        name: str,
        scan_name: str,
        id: str,
        native: str,
        logo: str,
        scan_token: str,
        scan_address: str,
        scan_tx: str,
        gas: str,
        dext: str,
        opensea: str,
        blockspan: str,
        tg: str,
        w3: str,
        com_multi: str,
        dao_multi: str
    ):
        self.live = live
        self.trading = trading
        self.name = name
        self.scan_name = scan_name
        self.id = id
        self.native = native
        self.logo = logo
        self.scan_token = scan_token
        self.scan_address = scan_address
        self.scan_tx = scan_tx
        self.gas = gas
        self.dext = dext
        self.opensea = opensea
        self.blockspan = blockspan
        self.tg = tg
        self.w3 = Web3(Web3.HTTPProvider(w3))
        self.com_multi = com_multi
        self.dao_multi = dao_multi

CHAINS = {
    "eth": ChainInfo(
        True,
        True,
        "ETH",
        "Etherscan",
        "1",
        "eth",
        media.ETH_LOGO,
        urls.SCAN_TOKEN("eth"),
        urls.SCAN_ADDRESS("eth"),
        urls.SCAN_TX("eth"),
        urls.SCAN_GAS("eth"),
        "ether",
        "",
        "eth-main",
        5,
        urls.RPC("eth"),
        ca.COM_MULTI("eth"),
        ca.DAO_MULTI("eth")
    ),
    "base": ChainInfo(
        True,
        False,
        "Base",
        "Basescan",
        "8453",
        "eth",
        media.BASE_LOGO,
        urls.SCAN_TOKEN("base"),
        urls.SCAN_ADDRESS("base"),
        urls.SCAN_TX("base"),
        urls.SCAN_GAS("eth"),
        "base",
        "-base",
        "base-main",
        2,
        urls.RPC("base"),
        ca.COM_MULTI("base"),
        ca.DAO_MULTI("base")
    ),
    "bsc": ChainInfo(
        True,
        False,
        "BSC",
        "BSCscan",
        "56",
        "bnb",
        media.BSC_LOGO,
        urls.SCAN_TOKEN("bsc"),
        urls.SCAN_ADDRESS("bsc"),
        urls.SCAN_TX("bsc"),
        urls.SCAN_GAS("bsc"),
        "bnb",
        "-binance",
        "",
        "",
        urls.RPC("bsc"),
        ca.COM_MULTI("bsc"),
        ca.DAO_MULTI("bsc")
    ),
    "arb": ChainInfo(
        True,
        False,
        "Arbitrum",
        "Arbiscan",
        "42161",
        "eth",
        media.ARB_LOGO,
        urls.SCAN_TOKEN("arb"),
        urls.SCAN_ADDRESS("arb"),
        urls.SCAN_TX("arb"),
        urls.SCAN_GAS("eth"),
        "arbitrum",
        "-arbitrum",
        "arbitrum-main",
        "",
        urls.RPC("arb"),
        ca.COM_MULTI("arb"),
        ca.DAO_MULTI("arb")
    ),
    "op": ChainInfo(
        True,
        False,
        "Optimism",
        "Optimisticscan",
        "10",
        "eth",
        media.OP_LOGO,
        urls.SCAN_TOKEN("op"),
        urls.SCAN_ADDRESS("op"),
        urls.SCAN_TX("op"),
        urls.SCAN_GAS("eth"),
        "optimism",
        "-optimism",
        "optimism-main",
        "",
        urls.RPC("op"),
        ca.COM_MULTI("op"),
        ca.DAO_MULTI("op")
    ),
    "poly": ChainInfo(
        True,
        False,
        "Polygon",
        "Polygonscan",
        "137",
        "pol",
        media.POLY_LOGO,
        urls.SCAN_TOKEN("poly"),
        urls.SCAN_ADDRESS("poly"),
        urls.SCAN_TX("poly"),
        urls.SCAN_GAS("poly"),
        "polygon",
        "-polygon",
        "poly-main",
        "",
        urls.RPC("poly"),
        ca.COM_MULTI("poly"),
        ca.DAO_MULTI("poly")
    )
}


GAS_CHAINS = ["eth", "poly", "bsc"]


def full_names():
    chain_names = [chain.name for chain in CHAINS.values()]
    return "\n".join(chain_names)


def short_names():
    chain_list = [key.upper() for key in CHAINS.keys()]
    return "\n".join(chain_list)


def get_chain(chat_id):
    for chain_name, chain_info in CHAINS.items():
        if chat_id == chain_info.tg:
            return chain_name
    return "eth"


def get_info(chain, token=None):
    if chain in CHAINS:
        chain_info = CHAINS[chain]

        if token and not chain_info.trading:
            return None, f"{chain_info.name} tokens not launched yet!"

        return chain_info, None
    else:
        return None, f'Chain not recognised, Please use one of the following abbreviations:\n\n{short_names()}'
