from hooks import db
from constants import ca, urls
from hooks import tools
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


MAINNETS = {
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
        False,
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
        797,
        urls.RPC("bsc"),
        ca.COM_MULTI("bsc"),
        ca.DAO_MULTI("bsc")
    ),
    "arb": ChainInfo(
        False,
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
        793,
        urls.RPC("arb"),
        ca.COM_MULTI("arb"),
        ca.DAO_MULTI("arb")
    ),
    "op": ChainInfo(
        False,
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
        795,
        urls.RPC("op"),
        ca.COM_MULTI("op"),
        ca.DAO_MULTI("op")
    ),
    "poly": ChainInfo(
        False,
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
        799,
        urls.RPC("poly"),
        ca.COM_MULTI("poly"),
        ca.DAO_MULTI("poly")
    )
}


TESTNETS = {
    "eth-sepolia": ChainInfo(
        True,
        False,
        "ETH Sepolia",
        "Etherscan Sepolia",
        "11155111",
        "eth",
        media.ETH_LOGO,
        urls.SCAN_TOKEN("eth-sepolia"),
        urls.SCAN_ADDRESS("eth-sepolia"),
        urls.SCAN_TX("eth-sepolia"),
        urls.SCAN_GAS("eth"),
        "ether",
        "",
        "eth-main",
        5,
        urls.RPC("eth-sepolia"),
        ca.COM_MULTI("eth-sepolia"),
        ca.DAO_MULTI("eth-sepolia")
    ),
    "base-sepolia": ChainInfo(
        True,
        False,
        "Base Sepolia",
        "Basescan Sepolia",
        "84532",
        "eth",
        media.BASE_LOGO,
        urls.SCAN_TOKEN("base-sepolia"),
        urls.SCAN_ADDRESS("base-sepolia"),
        urls.SCAN_TX("base-sepolia"),
        urls.SCAN_GAS("eth"),
        "base-testnet",
        "-base-testnet",
        "base-testnet",
        2,
        urls.RPC("base-sepolia"),
        ca.COM_MULTI("base-sepolia"),
        ca.DAO_MULTI("base-sepolia")
    ),
}


GAS_CHAINS = ["eth", "poly", "bsc"]


def active_chains():
    if tools.is_local():
        return {**MAINNETS, **TESTNETS}
    return {**MAINNETS, **TESTNETS} if db.settings_get("testnets") else MAINNETS


def full_names():
    chain_names = [chain.name for chain in MAINNETS.values()]
    return "\n".join(chain_names)


def get_chain(chat_id):
    for chain_name, chain_info in active_chains().items():
        if chat_id == chain_info.tg:
            return chain_name
    return "eth"


def get_info(chain, token=None):
    if chain in active_chains():
        chain_info = active_chains()[chain]

        if token and not chain_info.trading:
            return None, f"{chain_info.name} tokens not launched yet!"

        return chain_info, None
    else:
        return None, f'Chain not recognised, Please use one of the following abbreviations:\n\n{short_names()}'


def short_names():
    chain_list = [key.upper() for key in active_chains().keys()]
    return "\n".join(chain_list)