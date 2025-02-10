import os


def dex_tools_link(chain, address):
    return f"https://www.dextools.io/app/{chain}/pair-explorer/{address}"


def opensea_link(nft):
    link = "https://pro.opensea.io/collection/"
    map = {
        "eco": f"{link}x7-ecosystem-maxi",
        "liq": f"{link}x7-liquidity-maxi",
        "dex": f"{link}x7-dex-maxi",
        "borrow": f"{link}x7-borrowing-maxi",
        "magister": f"{link}x7-magister",
        "pioneer": f"{link}x7-pioneer",
    }
    return map.get(nft)


def rpc_link(chain):
    map = {
        "eth": f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_API_KEY')}",
        "bsc": f"https://lb.drpc.org/ogrpc?network=bsc&dkey={os.getenv('DRPC_API_KEY')}",
        "poly": f"https://lb.drpc.org/ogrpc?network=polygon&dkey={os.getenv('DRPC_API_KEY')}",
        "arb": f"https://lb.drpc.org/ogrpc?network=arbitrum&dkey={os.getenv('DRPC_API_KEY')}",
        "op": f"https://lb.drpc.org/ogrpc?network=optimism&dkey={os.getenv('DRPC_API_KEY')}",
        "base": f"https://lb.drpc.org/ogrpc?network=base&dkey={os.getenv('DRPC_API_KEY')}",
        "eth-sepolia": f"https://lb.drpc.org/ogrpc?network=sepolia&dkey={os.getenv('DRPC_API_KEY')}",
        "base-sepolia": f"https://lb.drpc.org/ogrpc?network=base-sepolia&dkey={os.getenv('DRPC_API_KEY')}",
    }
    return map.get(chain)


def scan_address(chain):
    map = {
        "eth": "https://etherscan.io/address/",
        "bsc": "https://bscscan.com/address/",
        "poly": "https://polygonscan.com/address/",
        "arb": "https://arbiscan.io/address/",
        "op": "https://optimistic.etherscan.io/address/",
        "base": "https://basescan.org/address/",
        "eth-sepolia": "https://sepolia.etherscan.io/address/",
        "base-sepolia": "https://sepolia.basescan.org/address/",
    }
    return map.get(chain)


def scan_gas(chain):
    map = {
        "eth": "https://etherscan.io/gastracker/",
        "bsc": "https://bscscan.com/gastracker/",
        "poly": "https://polygonscan.com/gastracker/",
    }
    return map.get(chain)


def scan_token(chain):
    map = {
        "eth": "https://etherscan.io/token/",
        "bsc": "https://bscscan.com/token/",
        "poly": "https://polygonscan.com/token/",
        "arb": "https://arbiscan.io/token/",
        "op": "https://optimistic.etherscan.io/token/",
        "base": "https://basescan.org/token/",
        "eth-sepolia": "https://sepolia.etherscan.io/token/",
        "base-sepolia": "https://sepolia.basescan.org/token/",
    }
    return map.get(chain)


def scan_tx(chain):
    map = {
        "eth": "https://etherscan.io/tx/",
        "bsc": "https://bscscan.com/tx/",
        "poly": "https://polygonscan.com/tx/",
        "arb": "https://arbiscan.io/tx/",
        "op": "https://optimistic.etherscan.io/tx/",
        "base": "https://basescan.org/tx/",
        "eth-sepolia": "https://sepolia.etherscan.io/tx/",
        "base-sepolia": "https://sepolia.basescan.org/tx/",
    }
    return map.get(chain)


def token_img_link(token):
    return f"https://assets.x7finance.org/images/tokens/{token}.png"


def xchange_buy_link(chain_id, token1):
    return f"https://x7finance.org/swap?chainId={chain_id}&token1={token1}"


TG_MAIN_CHANNEL_ID = "-1002417477914"
TG_ALERTS_CHANNEL_ID = "-1001942497316"
TG_ALERTS = "t.me/xchange_alerts"
TG_ANNOUNCEMENTS = "t.me/x7announcements"
TG_PORTAL = "t.me/x7portal"
TG_DAO = "https://telegram.me/collablandbot?start=VFBDI1RFTCNDT01NIy0xMDAyMTM5MTc4NTQx"
TG_XCHANGE_CREATE = "https://t.me/xchange_launcher_bot/"
TG_ALERTS_CHANNELS = {
    TG_MAIN_CHANNEL_ID: [(None, TG_ALERTS), (892, TG_ALERTS)],
    TG_ALERTS_CHANNEL_ID: [(None, TG_PORTAL)],
}

DUNE = "https://dune.com/mike_x7f/x7finance"
GITHUB = "https://github.com/x7finance/"
MEDIUM = "https://medium.com/@X7Finance"
PIONEERS = "https://assets.x7finance.org/pioneers/"
REDDIT = "https://www.reddit.com/r/x7finance"
SNAPSHOT = "https://snapshot.org/#/x7finance.eth"
TWITTER = "https://twitter.com/x7_finance/"
WARPCAST = "https://warpcast.com/x7finance"
WP_LINK = "https://assets.x7finance.org/pdf/whitepaper-1.1.pdf"
XCHANGE = "https://x7finance.org/"
