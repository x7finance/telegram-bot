from web3 import AsyncWeb3, Web3

from constants.bot import urls
from constants.protocol import addresses
from media import chain_logos
from utils import tools
from services import get_mysql

mysql = get_mysql()


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


def active_chains():
    if tools.is_local():
        return {**MAINNETS, **TESTNETS}
    return (
        {**MAINNETS, **TESTNETS}
        if mysql.settings_get("testnets")
        else MAINNETS
    )


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


MAINNETS = {
    "eth": ChainInfo(
        live=True,
        trading=True,
        name="ETH",
        scan_name="Etherscan",
        id="1",
        native="eth",
        logo=chain_logos.ETH_LOGO,
        scan_token=urls.scan_token("eth"),
        scan_address=urls.scan_address("eth"),
        scan_tx=urls.scan_tx("eth"),
        gas=urls.scan_gas("eth"),
        dext="ether",
        opensea="",
        blockspan="eth-main",
        tg=5,
        rpc_url=urls.rpc_link("eth"),
        com_multi=addresses.community_multi_sig("eth"),
        dao_multi=addresses.dao_multisig("eth"),
    ),
    "base": ChainInfo(
        live=True,
        trading=False,
        name="Base",
        scan_name="Basescan",
        id="8453",
        native="eth",
        logo=chain_logos.BASE_LOGO,
        scan_token=urls.scan_token("base"),
        scan_address=urls.scan_address("base"),
        scan_tx=urls.scan_tx("base"),
        gas=urls.scan_gas("eth"),
        dext="base",
        opensea="-base",
        blockspan="base-main",
        tg=2,
        rpc_url=urls.rpc_link("base"),
        com_multi=addresses.community_multi_sig("base"),
        dao_multi=addresses.dao_multisig("base"),
    ),
    "bsc": ChainInfo(
        live=False,
        trading=False,
        name="BSC",
        scan_name="BSCscan",
        id="56",
        native="bnb",
        logo=chain_logos.BSC_LOGO,
        scan_token=urls.scan_token("bsc"),
        scan_address=urls.scan_address("bsc"),
        scan_tx=urls.scan_tx("bsc"),
        gas=urls.scan_gas("bsc"),
        dext="bnb",
        opensea="-binance",
        blockspan="",
        tg=797,
        rpc_url=urls.rpc_link("bsc"),
        com_multi=addresses.community_multi_sig("bsc"),
        dao_multi=addresses.dao_multisig("bsc"),
    ),
    "arb": ChainInfo(
        live=False,
        trading=False,
        name="Arbitrum",
        scan_name="Arbiscan",
        id="42161",
        native="eth",
        logo=chain_logos.ARB_LOGO,
        scan_token=urls.scan_token("arb"),
        scan_address=urls.scan_address("arb"),
        scan_tx=urls.scan_tx("arb"),
        gas=urls.scan_gas("eth"),
        dext="arbitrum",
        opensea="-arbitrum",
        blockspan="arbitrum-main",
        tg=793,
        rpc_url=urls.rpc_link("arb"),
        com_multi=addresses.community_multi_sig("arb"),
        dao_multi=addresses.dao_multisig("arb"),
    ),
    "op": ChainInfo(
        live=False,
        trading=False,
        name="Optimism",
        scan_name="Optimisticscan",
        id="10",
        native="eth",
        logo=chain_logos.OP_LOGO,
        scan_token=urls.scan_token("op"),
        scan_address=urls.scan_address("op"),
        scan_tx=urls.scan_tx("op"),
        gas=urls.scan_gas("eth"),
        dext="optimism",
        opensea="-optimism",
        blockspan="optimism-main",
        tg=795,
        rpc_url=urls.rpc_link("op"),
        com_multi=addresses.community_multi_sig("op"),
        dao_multi=addresses.dao_multisig("op"),
    ),
    "poly": ChainInfo(
        live=False,
        trading=False,
        name="Polygon",
        scan_name="Polygonscan",
        id="137",
        native="pol",
        logo=chain_logos.POLY_LOGO,
        scan_token=urls.scan_token("poly"),
        scan_address=urls.scan_address("poly"),
        scan_tx=urls.scan_tx("poly"),
        gas=urls.scan_gas("poly"),
        dext="polygon",
        opensea="-polygon",
        blockspan="poly-main",
        tg=799,
        rpc_url=urls.rpc_link("poly"),
        com_multi=addresses.community_multi_sig("poly"),
        dao_multi=addresses.dao_multisig("poly"),
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
        logo=chain_logos.ETH_LOGO,
        scan_token=urls.scan_token("eth-sepolia"),
        scan_address=urls.scan_address("eth-sepolia"),
        scan_tx=urls.scan_tx("eth-sepolia"),
        gas=urls.scan_gas("eth"),
        dext="ether",
        opensea="",
        blockspan="eth-sepolia",
        tg=5,
        rpc_url=urls.rpc_link("eth-sepolia"),
        com_multi=addresses.community_multi_sig("eth-sepolia"),
        dao_multi=addresses.dao_multisig("eth-sepolia"),
    ),
    "base-sepolia": ChainInfo(
        live=True,
        trading=False,
        name="Base Sepolia",
        scan_name="Basescan Sepolia",
        id="84532",
        native="eth",
        logo=chain_logos.BASE_LOGO,
        scan_token=urls.scan_token("base-sepolia"),
        scan_address=urls.scan_address("base-sepolia"),
        scan_tx=urls.scan_tx("base-sepolia"),
        gas=urls.scan_gas("eth"),
        dext="base-testnet",
        opensea="-base-testnet",
        blockspan="base-testnet",
        tg=2,
        rpc_url=urls.rpc_link("base-sepolia"),
        com_multi=addresses.community_multi_sig("base-sepolia"),
        dao_multi=addresses.dao_multisig("base-sepolia"),
    ),
}


GAS_CHAINS = {"eth", "poly", "bsc"}
ETH_CHAINS = {"eth", "base", "arb", "op", "eth-sepolia", "base-sepolia"}
