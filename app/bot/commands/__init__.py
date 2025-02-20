from bot.commands import general, admin

GENERAL_HANDLERS = []
GENERAL_ALIAS = {
    "arbitrage": ["arb"],
    "constellations": ["quints", "x7100"],
    "hubs": ["hub"],
    "loans": ["loan"],
    "mcap": ["marketcap"],
    "pairs": ["pair"],
    "splitters": ["split", "splitter"],
    "top": ["trending"],
}

for func, description in [
    (general.about, "About X7 Finance"),
    (general.admins, "List of admins"),
    (general.alerts, "Xchange Alerts Channel"),
    (general.announcements, "Latest announcements"),
    (general.arbitrage, "Arbitrage opportunities"),
    (general.blocks, "Block info"),
    (general.blog, "Read the latest blog posts"),
    (general.borrow, "Loan rates"),
    (general.burn, "Burn info"),
    (general.buy, "Buy links"),
    (general.ca, "Contract addresses"),
    (general.channels, "X7 channels"),
    (general.chart, "Charts links"),
    (general.check, "Check valid input"),
    (general.compare, "Compare token metrics"),
    (general.constellations, "Constellations"),
    (general.contribute, "Contribute to X7"),
    (general.convert, "Convert token values"),
    (general.dao_command, "DAO info"),
    (general.docs, "View documentation"),
    (general.ecosystem, "View ecosystem tokens"),
    (general.factory, "Factory contracts"),
    (general.fg, "Market fear greed data"),
    (general.faq, "Frequently Asked Questions"),
    (general.feeto, "X7 FeeTo info"),
    (general.gas, "Check gas fees"),
    (general.github_command, "View GitHub repository"),
    (general.holders, "Check token holders"),
    (general.hubs, "View hubs and buybacks"),
    (general.leaderboard, "View leaderboard"),
    (general.links, "View important links"),
    (general.liquidate, "Liquidate loans"),
    (general.liquidity, "View liquidity details"),
    (general.loans, "Check active loans"),
    (general.locks, "View token locks"),
    (general.me, "Check your balance"),
    (general.mcap, "Check market cap"),
    (general.media_command, "View media links"),
    (general.nft, "View NFTs"),
    (general.onchains, "View onchain messages"),
    (general.pairs, "Check trading pairs"),
    (general.pioneer, "Pioneer information"),
    (general.pool, "View lending pool"),
    (general.price, "Check token prices"),
    (general.pushall, "Push X7 splitters"),
    (general.register, "Register a wallet"),
    (general.router, "View router contracts"),
    (general.smart, "X7 smart contracts"),
    (general.spaces, "Check available spaces"),
    (general.splitters_command, "View splitters"),
    (general.tax_command, "Check tax"),
    (general.timestamp_command, "Convert timestamps"),
    (general.time_command, "View system time"),
    (general.treasury, "View treasury details"),
    (general.top, "View trending tokens"),
    (general.twitter_command, "Twitter link"),
    (general.volume, "Check trading volume"),
    (general.wallet, "View wallet information"),
    (general.website, "Website link"),
    (general.wei, "Convert values to Wei"),
    (general.wp, "Read the whitepaper"),
    (general.x7r, "View X7R details"),
    (general.x7d, "View X7D details"),
    (general.x7dao, "View X7DAO details"),
    (general.x7101, "View X7101 details"),
    (general.x7102, "View X7102 details"),
    (general.x7103, "View X7103 details"),
    (general.x7104, "View X7104 details"),
    (general.x7105, "View X7105 details"),
    (general.x, "Xchange Price Bot"),
]:
    base_command = func.__name__.split("_")[0]
    commands = [base_command] + GENERAL_ALIAS.get(base_command, [])
    GENERAL_HANDLERS.append((commands, func, description))

GENERAL_HANDLERS.append(
    (["0xtrader"], general.twitter_command, "0xTrader Twitter link"),
)

ADMIN_HANDLERS = [
    (func.__name__.split("_")[0], func, description)
    for func, description in [
        (admin.settings_command, "Bot settings"),
        (admin.clickme, "Send Click Me!"),
        (admin.remove, "Remove an wallet"),
        (admin.status, "View bot status"),
        (admin.wen, "Next Click Me!"),
    ]
]
