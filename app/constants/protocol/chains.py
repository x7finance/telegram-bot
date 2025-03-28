from web3 import AsyncWeb3, WebSocketProvider
from web3.middleware import ExtraDataToPOAMiddleware

from constants.general import urls
from constants.protocol import addresses
from media import chain_logos
from utils import tools
from services import get_dbmanager

db = get_dbmanager()


ETH_CHAINS = {"eth", "base", "arb", "op", "eth-sepolia", "base-sepolia"}
POA_CHAINS = {"bsc", "poly"}
DEFAULT_CHAIN = "eth"


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
        tg: str,
        rpc_url: str,
        ws_rpc_url: str,
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
        self.tg = tg
        self.rpc_url = rpc_url
        self.ws_rpc_url = ws_rpc_url
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
        self.w3_ws = AsyncWeb3(WebSocketProvider(ws_rpc_url))
        self.com_multi = com_multi
        self.dao_multi = dao_multi

        if name.lower() in POA_CHAINS:
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            if self.w3_ws:
                self.w3_ws.middleware_onion.inject(
                    ExtraDataToPOAMiddleware, layer=0
                )


async def get_active_chains():
    if tools.is_local():
        return {**MAINNETS, **TESTNETS}
    return (
        {**MAINNETS, **TESTNETS}
        if await db.settings.get("testnets")
        else MAINNETS
    )


async def get_chain(chat_id):
    active_chains = await get_active_chains()
    for chain_name, chain_info in active_chains.items():
        if chat_id == chain_info.tg:
            return chain_name
    return DEFAULT_CHAIN


async def get_full_names():
    active_chains = await get_active_chains()
    chain_names = [chain.name for chain in active_chains.values()]
    return "\n".join(chain_names)


async def get_info(chain, token=None):
    active_chains = await get_active_chains()
    if chain in active_chains:
        chain_info = active_chains[chain]

        if token and not chain_info.trading:
            return None, f"{chain_info.name} tokens not launched yet!"

        return chain_info, None
    else:
        short_names = await get_short_names()
        return (
            None,
            f"Chain not recognised, Please use one of the following abbreviations:\n\n{short_names}",
        )


async def get_short_names():
    active_chains = await get_active_chains()
    chain_list = [key.upper() for key in active_chains.keys()]
    return "\n".join(chain_list)


MAINNETS = {
    "eth": ChainInfo(
        live=True,
        trading=True,
        name="ETH",
        scan_name="Etherscan",
        id=1,
        native="eth",
        logo=chain_logos.ETH_LOGO,
        scan_token=urls.scan_url("eth", "token"),
        scan_address=urls.scan_url("eth", "address"),
        scan_tx=urls.scan_url("eth", "tx"),
        gas=urls.scan_url("eth", "gas"),
        dext="ether",
        opensea="",
        tg=5,
        rpc_url=urls.rpc_link("eth"),
        ws_rpc_url=urls.rpc_link("eth", use_ws=True),
        com_multi=addresses.community_multi_sig("eth"),
        dao_multi=addresses.dao_multisig("eth"),
    ),
    "base": ChainInfo(
        live=True,
        trading=False,
        name="Base",
        scan_name="Basescan",
        id=8453,
        native="eth",
        logo=chain_logos.BASE_LOGO,
        scan_token=urls.scan_url("base", "token"),
        scan_address=urls.scan_url("base", "address"),
        scan_tx=urls.scan_url("base", "tx"),
        gas=urls.scan_url("eth", "gas"),
        dext="base",
        opensea="-base",
        tg=2,
        rpc_url=urls.rpc_link("base"),
        ws_rpc_url=urls.rpc_link("base", use_ws=True),
        com_multi=addresses.community_multi_sig("base"),
        dao_multi=addresses.dao_multisig("base"),
    ),
    "bsc": ChainInfo(
        live=False,
        trading=False,
        name="BSC",
        scan_name="BSCscan",
        id=56,
        native="bnb",
        logo=chain_logos.BSC_LOGO,
        scan_token=urls.scan_url("bsc", "token"),
        scan_address=urls.scan_url("bsc", "address"),
        scan_tx=urls.scan_url("bsc", "tx"),
        gas=urls.scan_url("bsc", "gas"),
        dext="bnb",
        opensea="-binance",
        tg=797,
        rpc_url=urls.rpc_link("bsc"),
        ws_rpc_url=urls.rpc_link("bsc", use_ws=True),
        com_multi=addresses.community_multi_sig("bsc"),
        dao_multi=addresses.dao_multisig("bsc"),
    ),
    "arb": ChainInfo(
        live=False,
        trading=False,
        name="Arbitrum",
        scan_name="Arbiscan",
        id=42161,
        native="eth",
        logo=chain_logos.ARB_LOGO,
        scan_token=urls.scan_url("arb", "token"),
        scan_address=urls.scan_url("arb", "address"),
        scan_tx=urls.scan_url("arb", "tx"),
        gas=urls.scan_url("eth", "gas"),
        dext="arbitrum",
        opensea="-arbitrum",
        tg=793,
        rpc_url=urls.rpc_link("arb"),
        ws_rpc_url=urls.rpc_link("arb", use_ws=True),
        com_multi=addresses.community_multi_sig("arb"),
        dao_multi=addresses.dao_multisig("arb"),
    ),
    "op": ChainInfo(
        live=False,
        trading=False,
        name="Optimism",
        scan_name="Optimisticscan",
        id=10,
        native="eth",
        logo=chain_logos.OP_LOGO,
        scan_token=urls.scan_url("op", "token"),
        scan_address=urls.scan_url("op", "address"),
        scan_tx=urls.scan_url("op", "tx"),
        gas=urls.scan_url("eth", "gas"),
        dext="optimism",
        opensea="-optimism",
        tg=795,
        rpc_url=urls.rpc_link("op"),
        ws_rpc_url=urls.rpc_link("op", use_ws=True),
        com_multi=addresses.community_multi_sig("op"),
        dao_multi=addresses.dao_multisig("op"),
    ),
    "poly": ChainInfo(
        live=False,
        trading=False,
        name="Polygon",
        scan_name="Polygonscan",
        id=137,
        native="pol",
        logo=chain_logos.POLY_LOGO,
        scan_token=urls.scan_url("poly", "token"),
        scan_address=urls.scan_url("poly", "address"),
        scan_tx=urls.scan_url("poly", "tx"),
        gas=urls.scan_url("poly", "gas"),
        dext="polygon",
        opensea="-polygon",
        tg=799,
        rpc_url=urls.rpc_link("poly"),
        ws_rpc_url=urls.rpc_link("poly", use_ws=True),
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
        id=11155111,
        native="eth",
        logo=chain_logos.ETH_LOGO,
        scan_token=urls.scan_url("eth-sepolia", "token"),
        scan_address=urls.scan_url("eth-sepolia", "address"),
        scan_tx=urls.scan_url("eth-sepolia", "tx"),
        gas=urls.scan_url("eth", "gas"),
        dext="ether",
        opensea="",
        tg=5,
        rpc_url=urls.rpc_link("eth-sepolia"),
        ws_rpc_url=urls.rpc_link("eth-sepolia", use_ws=True),
        com_multi=addresses.community_multi_sig("eth-sepolia"),
        dao_multi=addresses.dao_multisig("eth-sepolia"),
    ),
    "base-sepolia": ChainInfo(
        live=True,
        trading=False,
        name="Base Sepolia",
        scan_name="Basescan Sepolia",
        id=84532,
        native="eth",
        logo=chain_logos.BASE_LOGO,
        scan_token=urls.scan_url("base-sepolia", "token"),
        scan_address=urls.scan_url("base-sepolia", "address"),
        scan_tx=urls.scan_url("base-sepolia", "tx"),
        gas=urls.scan_url("eth", "gas"),
        dext="base-testnet",
        opensea="-base-testnet",
        tg=2,
        rpc_url=urls.rpc_link("base-sepolia"),
        ws_rpc_url=urls.rpc_link("base-sepolia", use_ws=True),
        com_multi=addresses.community_multi_sig("base-sepolia"),
        dao_multi=addresses.dao_multisig("base-sepolia"),
    ),
}
