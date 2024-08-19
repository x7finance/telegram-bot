# CHAINS

import os
from constants import ca, urls
import media


class ChainInfo:
    def __init__(
        self,
        live: bool,
        name: str,
        scan_name: str,
        id: str,
        token: str,
        logo: str,
        scan_token: str,
        scan_address: str,
        scan_tx: str,
        gas: str,
        dext: str,
        opensea: str,
        blockspan: str,
        w3: str,
        api: str,
        key: str,
        com_multi: str,
        dao_multi: str,
        pairs: list
    ):
        self.live = live
        self.name = name
        self.scan_name = scan_name
        self.id = id
        self.token = token
        self.logo = logo
        self.scan_token = scan_token
        self.scan_address = scan_address
        self.scan_tx = scan_tx
        self.gas = gas
        self.dext = dext
        self.opensea = opensea
        self.blockspan = blockspan
        self.w3 = w3
        self.api = api
        self.key = key
        self.com_multi = com_multi
        self.dao_multi = dao_multi
        self.pairs = pairs


CHAINS = {
    "eth": ChainInfo(
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
        urls.RPC("eth"),
        urls.SCAN_API("eth"),
        os.getenv('ETHER'),
        ca.COM_MULTI("eth"),
        ca.DAO_MULTI("eth"), 
        [ca.X7R_PAIR("eth"),
        ca.X7DAO_PAIR("eth"),
        ca.X7101_PAIR("eth"),
        ca.X7102_PAIR("eth"),
        ca.X7103_PAIR("eth"),
        ca.X7104_PAIR("eth"),
        ca.X7105_PAIR("eth")]
    ),
    "base": ChainInfo(
        True,
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
        urls.RPC("base"),
        urls.SCAN_API("base"),
        os.getenv('BASE'),
        ca.COM_MULTI("base"),
        ca.DAO_MULTI("base"), 
        [ca.X7R_PAIR("base"),
        ca.X7DAO_PAIR("base"),
        ca.X7101_PAIR("base"),
        ca.X7102_PAIR("base"),
        ca.X7103_PAIR("base"),
        ca.X7104_PAIR("base"),
        ca.X7105_PAIR("base")]
    ),
    "bsc": ChainInfo(
        True,
        "BSC",
        "BSCscan",
        "56",
        "bnb",
        media.BSC_LOGO,
        urls.SCAN_TOKEN("bsc"),
        urls.SCAN_ADDRESS("bsc"),
        urls.SCAN_TX("bsc"),
        urls.SCAN_GAS("bsc"),
        "bsc",
        "-binance",
        "",
        urls.RPC("bsc"),
        urls.SCAN_API("bsc"),
        os.getenv('BSC'),
        ca.COM_MULTI("bsc"),
        ca.DAO_MULTI("bsc"), 
        [ca.X7R_PAIR("bsc"),
        ca.X7DAO_PAIR("bsc"),
        ca.X7101_PAIR("bsc"),
        ca.X7102_PAIR("bsc"),
        ca.X7103_PAIR("bsc"),
        ca.X7104_PAIR("bsc"),
        ca.X7105_PAIR("bsc")]
    ),
    "arb": ChainInfo(
        True,
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
        urls.RPC("arb"),
        urls.SCAN_API("arb"),
        os.getenv('ARB'),
        ca.COM_MULTI("arb"),
        ca.DAO_MULTI("arb"), 
        [ca.X7R_PAIR("arb"),
        ca.X7DAO_PAIR("arb"),
        ca.X7101_PAIR("arb"),
        ca.X7102_PAIR("arb"),
        ca.X7103_PAIR("arb"),
        ca.X7104_PAIR("arb"),
        ca.X7105_PAIR("arb")]
    ),
    "op": ChainInfo(
        True,
        "Optimism",
        "Optimisticscan",
        "10",
        "eth",
        media.OPTI_LOGO,
        urls.SCAN_TOKEN("op"),
        urls.SCAN_ADDRESS("op"),
        urls.SCAN_TX("op"),
        urls.SCAN_GAS("eth"),
        "optimism",
        "-optimism",
        "optimism-main",
        urls.RPC("op"),
        urls.SCAN_API("op"),
        os.getenv('OP'),
        ca.COM_MULTI("op"),
        ca.DAO_MULTI("op"), 
        [ca.X7R_PAIR("op"),
        ca.X7DAO_PAIR("op"),
        ca.X7101_PAIR("op"),
        ca.X7102_PAIR("op"),
        ca.X7103_PAIR("op"),
        ca.X7104_PAIR("op"),
        ca.X7105_PAIR("op")]
    ),
    "poly": ChainInfo(
        True,
        "Polygon",
        "Polygonscan",
        "137",
        "matic",
        media.POLY_LOGO,
        urls.SCAN_TOKEN("poly"),
        urls.SCAN_ADDRESS("poly"),
        urls.SCAN_TX("poly"),
        urls.SCAN_GAS("poly"),
        "polygon",
        "-polygon",
        "poly-main",
        urls.RPC("poly"),
        urls.SCAN_API("poly"),
        os.getenv('POLY'),
        ca.COM_MULTI("poly"),
        ca.DAO_MULTI("poly"), 
        [ca.X7R_PAIR("poly"),
        ca.X7DAO_PAIR("poly"),
        ca.X7101_PAIR("poly"),
        ca.X7102_PAIR("poly"),
        ca.X7103_PAIR("poly"),
        ca.X7104_PAIR("poly"),
        ca.X7105_PAIR("poly")]
    )
}


GAS_CHAINS = ["eth", "poly", "bsc"]
INITIAL_LIQ = ["op", "bsc", "arb", "poly"]


def DEFAULT_CHAIN(chat_id):
    if chat_id == int(os.getenv("BASE_TELEGRAM_CHANNEL_ID")):
        return "base"
    else:
        return "eth"


def FULL_NAMES():
    chain_names = [chain.name for chain in CHAINS.values()]
    return "\n".join(chain_names)


def SHORT_NAMES():
    chain_list = list(CHAINS.keys())
    return "\n".join(chain_list)
