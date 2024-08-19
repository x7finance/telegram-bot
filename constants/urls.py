import os

def SCAN_API(chain):
    if chain == "eth":
        return "https://api.etherscan.io/api"
    if chain == "bsc":
        return "https://api.bscscan.com/api"
    if chain == "poly":
        return "https://api.polygonscan.com/api"
    if chain == "arb":
        return "https://api.arbiscan.io/api"
    if chain == "op":
        return "https://api-optimistic.etherscan.io/api"
    if chain == "base":
        return "https://api.basescan.org/api"
    

def SCAN_TOKEN(chain):
    if chain == "eth":
        return "https://etherscan.io/token/"
    if chain == "bsc":
        return "https://bscscan.com/token/"
    if chain == "poly":
        return "https://polygonscan.com/token/"
    if chain == "arb":
        return "https://arbiscan.io/token/"
    if chain == "op":
        return "https://optimistic.etherscan.io/token/"
    if chain == "base":
        return "https://basescan.org/token/"


def SCAN_ADDRESS(chain):
    if chain == "eth":
        return "https://etherscan.io/address/"
    if chain == "bsc":
        return "https://bscscan.com/address/"
    if chain == "poly":
        return "https://polygonscan.com/address/"
    if chain == "arb":
        return "https://arbiscan.io/address/"
    if chain == "op":
        return "https://optimistic.etherscan.io/address/"
    if chain == "base":
        return "https://basescan.org/address/"
    

def SCAN_TX(chain):
    if chain == "eth":
        return "https://etherscan.io/tx/"
    if chain == "bsc":
        return "https://bscscan.com/tx/"
    if chain == "poly":
        return "https://polygonscan.com/tx/"
    if chain == "arb":
        return "https://arbiscan.io/tx/"
    if chain == "op":
        return "https://optimistic.etherscan.io/tx/"
    if chain == "base":
        return "https://basescan.org/tx/"


def SCAN_GAS(chain):
    if chain == "eth":
        return "https://etherscan.io/gastracker/"
    if chain == "bsc":
        return "https://bscscan.com/gastracker/"
    if chain == "poly":
        return "https://polygonscan.com/gastracker/"


def DEX_TOOLS(chain):
    return f"https://www.dextools.io/app/{chain}/pair-explorer/"


def RPC(chain):
    if chain == "eth":
        return f"https://lb.drpc.org/ogrpc?network=ethereum&dkey={os.getenv('DRPC_API_KEY')}"
    if chain == "bsc":
        return f"https://lb.drpc.org/ogrpc?network=bsc&dkey={os.getenv('DRPC_API_KEY')}"
    if chain == "poly":
        return f"https://lb.drpc.org/ogrpc?network=polygon&dkey={os.getenv('DRPC_API_KEY')}"
    if chain == "arb":
        return f"https://lb.drpc.org/ogrpc?network=arbitrum&dkey={os.getenv('DRPC_API_KEY')}"
    if chain == "op":
        return f"https://lb.drpc.org/ogrpc?network=optimism&dkey={os.getenv('DRPC_API_KEY')}"
    if chain == "base":
        return f"https://lb.drpc.org/ogrpc?network=base&dkey={os.getenv('DRPC_API_KEY')}"


def XCHANGE_BUY(chain_id, token1):
    return f"https://x7finance.org/?chainId={chain_id}&token1={token1}"


def OS_LINK(nft):
    link = "https://pro.opensea.io/collection/"
    if nft == "eco":
        return f"{link}x7-ecosystem-maxi"
    if nft == "liq":
        return f"{link}x7-liquidity-maxi"
    if nft == "dex":
        return f"{link}x7-dex-maxi"
    if nft == "borrow":
        return f"{link}x7-borrowing-maxi"
    if nft == "magister":
        return f"{link}x7-magister"
    if nft == "pioneer":
        return f"{link}x7-pioneer"


# TG
TG_MAIN = "t.me/x7m105portal"
TG_BASE = "t.me/x7portal"
TG_ALERTS = "t.me/xchange_alerts"
TG_ANNOUNCEMENTS = "t.me/x7announcements"
TG_DAO = "https://telegram.me/collablandbot?start=VFBDI1RFTCNDT01NIy0xMDAyMTM5MTc4NTQx"


# LINKS
CA_DIRECTORY = "https://www.x7finance.org/en/docs/breakdowns/contracts"
DISCORD = "https://discord.gg/x7finance"
DUNE = "https://dune.com/mike_x7f/x7finance"
GITHUB = "https://github.com/x7finance/"
MEDIUM = "https://medium.com/@X7Finance"
PIONEERS = "https://img.x7.finance/pioneers/"
REDDIT = "https://www.reddit.com/r/x7finance"
SNAPSHOT = "https://snapshot.org/#/x7finance.eth"
TWITTER = "https://twitter.com/x7_finance/"
WARPCAST = "https://warpcast.com/x7finance"
WP_LINK = "https://x7.finance/wp/v1_1_0/X7FinanceWhitepaper.pdf"
XCHANGE = "https://x7finance.org/"
