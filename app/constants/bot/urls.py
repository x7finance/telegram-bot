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


def rpc_link(chain, use_ws=False):
    protocol = "wss" if use_ws else "https"
    path = "ogws" if use_ws else "ogrpc"

    map = {
        "eth": f"{protocol}://lb.drpc.org/{path}?network=ethereum&dkey={os.getenv('DRPC_API_KEY')}",
        "bsc": f"{protocol}://lb.drpc.org/{path}?network=bsc&dkey={os.getenv('DRPC_API_KEY')}",
        "poly": f"{protocol}://lb.drpc.org/{path}?network=polygon&dkey={os.getenv('DRPC_API_KEY')}",
        "arb": f"{protocol}://lb.drpc.org/{path}?network=arbitrum&dkey={os.getenv('DRPC_API_KEY')}",
        "op": f"{protocol}://lb.drpc.org/{path}?network=optimism&dkey={os.getenv('DRPC_API_KEY')}",
        "base": f"{protocol}://lb.drpc.org/{path}?network=base&dkey={os.getenv('DRPC_API_KEY')}",
        "eth-sepolia": f"{protocol}://lb.drpc.org/{path}?network=sepolia&dkey={os.getenv('DRPC_API_KEY')}",
        "base-sepolia": f"{protocol}://lb.drpc.org/{path}?network=base-sepolia&dkey={os.getenv('DRPC_API_KEY')}",
    }
    return map.get(chain)


def scan_url(chain, category):
    map = {
        "eth": "https://etherscan.io/",
        "bsc": "https://bscscan.com/",
        "poly": "https://polygonscan.com/",
        "arb": "https://arbiscan.io/",
        "op": "https://optimistic.etherscan.io/",
        "base": "https://basescan.org/",
        "eth-sepolia": "https://sepolia.etherscan.io/",
        "base-sepolia": "https://sepolia.basescan.org/",
    }

    categories = {
        "address": "address/",
        "gas": "gastracker/",
        "token": "token/",
        "tx": "tx/",
    }

    base_url = map.get(chain)
    category_path = categories.get(category)

    return base_url + category_path


def token_img_link(token):
    return f"https://assets.x7finance.org/images/tokens/{token}.png"


def xchange_buy_link(chain_id, token1):
    return f"https://x7finance.org/swap?chainId={chain_id}&token1={token1}"


TG_MAIN_CHANNEL_ID = "-1002417477914"
TG_ALERTS_CHANNEL_ID = "-1001942497316"

TG_ALERTS = "t.me/xchange_alerts"
TG_PORTAL = "t.me/x7portal"
TG_XCHANGE_CREATE = "t.me/xchange_launcher_bot"
TG_XCHANGE_PRICE_BOT = "t.me/xchange_price_bot"

TG_ALERTS_CHANNELS = {
    TG_MAIN_CHANNEL_ID: [(None, TG_ALERTS), (892, TG_ALERTS)],
    TG_ALERTS_CHANNEL_ID: [(None, TG_PORTAL)],
}

DUNE = "https://dune.com/mike_x7f/x7finance"
GITHUB = "https://github.com/x7finance/"
GITHUB_BOT = "https://github.com/x7finance/telegram-bot"
MEDIUM = "https://medium.com/@X7Finance"
PIONEERS = "https://assets.x7finance.org/pioneers/"
REDDIT = "https://www.reddit.com/r/x7finance"
SNAPSHOT = "https://snapshot.org/#/x7finance.eth"
TWITTER = "https://twitter.com/x7_finance/"
WARPCAST = "https://warpcast.com/x7finance"
WP_LINK = "https://assets.x7finance.org/pdf/whitepaper-1.1.pdf"
XCHANGE = "https://x7finance.org/"
