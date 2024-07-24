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
        dev_multi: str,
        dao_multi: str,
        pairs: list,
        paired_token: str
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
        self.dev_multi = dev_multi
        self.dao_multi = dao_multi
        self.pairs = pairs
        self.paired_token = paired_token


CHAINS = {
    "eth": ChainInfo(
        True,
        "ETH",
        "Etherscan",
        "1",
        "eth",
        media.ETH_LOGO,
        urls.ETHER_TOKEN,
        urls.ETHER_ADDRESS,
        urls.ETHER_TX,
        urls.ETHER_GAS,
        "ether",
        "",
        "eth-main",
        urls.ETH_RPC,
        urls.ETHER_API,
        os.getenv('ETHER'),
        ca.COM_MULTI_ETH,
        ca.DEV_MULTI_ETH,
        ca.DAO_MULTI_ETH, 
        [ca.X7R_PAIR_ETH,
        ca.X7DAO_PAIR_ETH,
        ca.X7101_PAIR_ETH,
        ca.X7102_PAIR_ETH,
        ca.X7103_PAIR_ETH,
        ca.X7104_PAIR_ETH,
        ca.X7105_PAIR_ETH],
        ca.WETH
    ),
    "base": ChainInfo(
        True,
        "Base",
        "Basescan",
        "8453",
        "eth",
        media.BASE_LOGO,
        urls.BASE_TOKEN,
        urls.BASE_ADDRESS,
        urls.BASE_TX,
        urls.ETHER_GAS,
        "base",
        "-base",
        "base-main",
        urls.BASE_RPC,
        urls.BASE_API,
        os.getenv('BASE'),
        ca.COM_MULTI_BASE,
        ca.DEV_MULTI_BASE,
        ca.DAO_MULTI_BASE, 
        [ca.X7R_PAIR_BASE,
        ca.X7DAO_PAIR_BASE,
        ca.X7101_PAIR_BASE,
        ca.X7102_PAIR_BASE,
        ca.X7103_PAIR_BASE,
        ca.X7104_PAIR_BASE,
        ca.X7105_PAIR_BASE],
        ca.CBETH
    ),
    "bsc": ChainInfo(
        True,
        "BSC",
        "BSCscan",
        "56",
        "bnb",
        media.BSC_LOGO,
        urls.BSC_TOKEN,
        urls.BSC_ADDRESS,
        urls.BSC_TX,
        urls.BSC_GAS,
        "bsc",
        "-binance",
        "",
        urls.BSC_RPC,
        urls.BSC_API,
        os.getenv('BSC'),
        ca.COM_MULTI_BSC,
        ca.DEV_MULTI_BSC,
        ca.DAO_MULTI_BSC, 
        [ca.X7R_PAIR_BSC,
        ca.X7DAO_PAIR_BSC,
        ca.X7101_PAIR_BSC,
        ca.X7102_PAIR_BSC,
        ca.X7103_PAIR_BSC,
        ca.X7104_PAIR_BSC,
        ca.X7105_PAIR_BSC],
        ca.WBNB
    ),
    "arb": ChainInfo(
        True,
        "Arbitrum",
        "Arbiscan",
        "42161",
        "eth",
        media.ARB_LOGO,
        urls.ARB_TOKEN,
        urls.ARB_ADDRESS,
        urls.ARB_TX,
        urls.ETHER_GAS,
        "arbitrum",
        "-arbitrum",
        "arbitrum-main",
        urls.ARB_RPC,
        urls.ARB_API,
        os.getenv('ARB'),
        ca.COM_MULTI_ARB,
        ca.DEV_MULTI_ARB,
        ca.DAO_MULTI_ARB, 
        [ca.X7R_PAIR_ARB,
        ca.X7DAO_PAIR_ARB,
        ca.X7101_PAIR_ARB,
        ca.X7102_PAIR_ARB,
        ca.X7103_PAIR_ARB,
        ca.X7104_PAIR_ARB,
        ca.X7105_PAIR_ARB,],
        ca.AWETH
        
    ),
    "op": ChainInfo(
        True,
        "Optimism",
        "Optimisticscan",
        "10",
        "eth",
        media.OPTI_LOGO,
        urls.OP_TOKEN,
        urls.OP_ADDRESS,
        urls.OP_TX,
        urls.ETHER_GAS,
        "optimism",
        "-optimism",
        "optimism-main",
        urls.OP_RPC,
        urls.OP_API,
        os.getenv('OP'),
        ca.COM_MULTI_OP,
        ca.DEV_MULTI_OP,
        ca.DAO_MULTI_OP, 
        [ca.X7R_PAIR_OP,
        ca.X7DAO_PAIR_OP,
        ca.X7101_PAIR_OP,
        ca.X7102_PAIR_OP,
        ca.X7103_PAIR_OP,
        ca.X7104_PAIR_OP,
        ca.X7105_PAIR_OP],
        ca.OWETH
    ),
    "poly": ChainInfo(
        True,
        "Polygon",
        "Polygonscan",
        "137",
        "matic",
        media.POLY_LOGO,
        urls.POLY_TOKEN,
        urls.POLY_ADDRESS,
        urls.POLY_TX,
        urls.POLY_GAS,
        "polygon",
        "-polygon",
        "poly-main",
        urls.POLY_RPC,
        urls.POLY_API,
        os.getenv('POLY'),
        ca.COM_MULTI_POLY,
        ca.DEV_MULTI_POLY,
        ca.DAO_MULTI_POLY, 
        [ca.X7R_PAIR_POLY,
        ca.X7DAO_PAIR_POLY,
        ca.X7101_PAIR_POLY,
        ca.X7102_PAIR_POLY,
        ca.X7103_PAIR_POLY,
        ca.X7104_PAIR_POLY,
        ca.X7105_PAIR_POLY],
        ca.WMATIC
    )
}


GAS_CHAINS = ["eth", "poly", "bsc"]
INITIAL_LIQ = ["op", "bsc", "arb", "poly"]


def default_chain(chat_id):
    if chat_id == int(os.getenv("BASE_TELEGRAM_CHANNEL_ID")):
        return "base"
    else:
        return "eth"


def full_names():
    chain_names = [chain.name for chain in CHAINS.values()]
    return "\n".join(chain_names)


def short_names():
    chain_list = list(CHAINS.keys())
    return "\n".join(chain_list)
