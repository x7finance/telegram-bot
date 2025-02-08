from hooks import db
from constants import ca, urls
from hooks import tools
from media import images

from web3 import AsyncWeb3, Web3


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
        rpc_url: str,
        com_multi: str,
        dao_multi: str,
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
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.w3async = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
        self.com_multi = com_multi
        self.dao_multi = dao_multi


MAINNETS = {
    "eth": ChainInfo(
        live=True,
        trading=True,
        name="ETH",
        scan_name="Etherscan",
        id="1",
        native="eth",
        logo=images.ETH_LOGO,
        scan_token=urls.SCAN_TOKEN("eth"),
        scan_address=urls.SCAN_ADDRESS("eth"),
        scan_tx=urls.SCAN_TX("eth"),
        gas=urls.SCAN_GAS("eth"),
        dext="ether",
        opensea="",
        blockspan="eth-main",
        tg=5,
        rpc_url=urls.RPC("eth"),
        com_multi=ca.COM_MULTI("eth"),
        dao_multi=ca.DAO_MULTI("eth"),
    ),
    "base": ChainInfo(
        live=True,
        trading=False,
        name="Base",
        scan_name="Basescan",
        id="8453",
        native="eth",
        logo=images.BASE_LOGO,
        scan_token=urls.SCAN_TOKEN("base"),
        scan_address=urls.SCAN_ADDRESS("base"),
        scan_tx=urls.SCAN_TX("base"),
        gas=urls.SCAN_GAS("eth"),
        dext="base",
        opensea="-base",
        blockspan="base-main",
        tg=2,
        rpc_url=urls.RPC("base"),
        com_multi=ca.COM_MULTI("base"),
        dao_multi=ca.DAO_MULTI("base"),
    ),
    "bsc": ChainInfo(
        live=False,
        trading=False,
        name="BSC",
        scan_name="BSCscan",
        id="56",
        native="bnb",
        logo=images.BSC_LOGO,
        scan_token=urls.SCAN_TOKEN("bsc"),
        scan_address=urls.SCAN_ADDRESS("bsc"),
        scan_tx=urls.SCAN_TX("bsc"),
        gas=urls.SCAN_GAS("bsc"),
        dext="bnb",
        opensea="-binance",
        blockspan="",
        tg=797,
        rpc_url=urls.RPC("bsc"),
        com_multi=ca.COM_MULTI("bsc"),
        dao_multi=ca.DAO_MULTI("bsc"),
    ),
    "arb": ChainInfo(
        live=False,
        trading=False,
        name="Arbitrum",
        scan_name="Arbiscan",
        id="42161",
        native="eth",
        logo=images.ARB_LOGO,
        scan_token=urls.SCAN_TOKEN("arb"),
        scan_address=urls.SCAN_ADDRESS("arb"),
        scan_tx=urls.SCAN_TX("arb"),
        gas=urls.SCAN_GAS("eth"),
        dext="arbitrum",
        opensea="-arbitrum",
        blockspan="arbitrum-main",
        tg=793,
        rpc_url=urls.RPC("arb"),
        com_multi=ca.COM_MULTI("arb"),
        dao_multi=ca.DAO_MULTI("arb"),
    ),
    "op": ChainInfo(
        live=False,
        trading=False,
        name="Optimism",
        scan_name="Optimisticscan",
        id="10",
        native="eth",
        logo=images.OP_LOGO,
        scan_token=urls.SCAN_TOKEN("op"),
        scan_address=urls.SCAN_ADDRESS("op"),
        scan_tx=urls.SCAN_TX("op"),
        gas=urls.SCAN_GAS("eth"),
        dext="optimism",
        opensea="-optimism",
        blockspan="optimism-main",
        tg=795,
        rpc_url=urls.RPC("op"),
        com_multi=ca.COM_MULTI("op"),
        dao_multi=ca.DAO_MULTI("op"),
    ),
    "poly": ChainInfo(
        live=False,
        trading=False,
        name="Polygon",
        scan_name="Polygonscan",
        id="137",
        native="pol",
        logo=images.POLY_LOGO,
        scan_token=urls.SCAN_TOKEN("poly"),
        scan_address=urls.SCAN_ADDRESS("poly"),
        scan_tx=urls.SCAN_TX("poly"),
        gas=urls.SCAN_GAS("poly"),
        dext="polygon",
        opensea="-polygon",
        blockspan="poly-main",
        tg=799,
        rpc_url=urls.RPC("poly"),
        com_multi=ca.COM_MULTI("poly"),
        dao_multi=ca.DAO_MULTI("poly"),
    ),
}


TESTNETS = {
    "eth-sepolia": ChainInfo(
        live=True,
        trading=False,
        name="ETH Sepolia",
        scan_name="Etherscan Sepolia",
        id="11155111",
        native="eth",
        logo=images.ETH_LOGO,
        scan_token=urls.SCAN_TOKEN("eth-sepolia"),
        scan_address=urls.SCAN_ADDRESS("eth-sepolia"),
        scan_tx=urls.SCAN_TX("eth-sepolia"),
        gas=urls.SCAN_GAS("eth"),
        dext="ether",
        opensea="",
        blockspan="eth-sepolia",
        tg=5,
        rpc_url=urls.RPC("eth-sepolia"),
        com_multi=ca.COM_MULTI("eth-sepolia"),
        dao_multi=ca.DAO_MULTI("eth-sepolia"),
    ),
    "base-sepolia": ChainInfo(
        live=True,
        trading=False,
        name="Base Sepolia",
        scan_name="Basescan Sepolia",
        id="84532",
        native="eth",
        logo=images.BASE_LOGO,
        scan_token=urls.SCAN_TOKEN("base-sepolia"),
        scan_address=urls.SCAN_ADDRESS("base-sepolia"),
        scan_tx=urls.SCAN_TX("base-sepolia"),
        gas=urls.SCAN_GAS("eth"),
        dext="base-testnet",
        opensea="-base-testnet",
        blockspan="base-testnet",
        tg=2,
        rpc_url=urls.RPC("base-sepolia"),
        com_multi=ca.COM_MULTI("base-sepolia"),
        dao_multi=ca.DAO_MULTI("base-sepolia"),
    ),
}


GAS_CHAINS = ["eth", "poly", "bsc"]

ETH_CHAINS = {"eth", "base", "arb", "op", "eth-sepolia", "base-sepolia"}


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
        return (
            None,
            f"Chain not recognised, Please use one of the following abbreviations:\n\n{short_names()}",
        )


def short_names():
    chain_list = [key.upper() for key in active_chains().keys()]
    return "\n".join(chain_list)
