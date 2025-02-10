from constants.protocol import addresses, chains
from media import token_logos


class TokensInfo:
    def __init__(
        self, name: str, ca: str, pairs: str | list, hub: str, logo: str
    ):
        self.name = name
        self.ca = ca
        self.pairs = pairs
        self.hub = hub
        self.logo = logo


def get_tokens():
    return {
        "x7dao": {
            chain: TokensInfo(
                "X7DAO",
                addresses.x7dao(chain),
                addresses.x7dao_pair(chain),
                addresses.x7dao_liquidity_hub(chain),
                token_logos.X7DAO_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7r": {
            chain: TokensInfo(
                "X7R",
                addresses.x7r(chain),
                addresses.x7r_pair(chain),
                addresses.x7r_liquidity_hub(chain),
                token_logos.X7R_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7101": {
            chain: TokensInfo(
                "X7101",
                addresses.x7101(chain),
                addresses.x7101_pair(chain),
                addresses.x7100_liquidity_hub(chain),
                token_logos.X7101_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7102": {
            chain: TokensInfo(
                "X7102",
                addresses.x7102(chain),
                addresses.x7102_pair(chain),
                addresses.x7100_liquidity_hub(chain),
                token_logos.X7102_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7103": {
            chain: TokensInfo(
                "X7103",
                addresses.x7103(chain),
                addresses.x7103_pair(chain),
                addresses.x7100_liquidity_hub(chain),
                token_logos.X7103_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7104": {
            chain: TokensInfo(
                "X7104",
                addresses.x7104(chain),
                addresses.x7104_pair(chain),
                addresses.x7100_liquidity_hub(chain),
                token_logos.X7104_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7105": {
            chain: TokensInfo(
                "X7105",
                addresses.x7105(chain),
                addresses.x7105_pair(chain),
                addresses.x7100_liquidity_hub(chain),
                token_logos.X7105_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7D": {
            chain: TokensInfo(
                "X7D", addresses.x7d(chain), None, None, token_logos.X7D_LOGO
            )
            for chain in chains.get_active_chains()
        },
    }


BLUE_CHIPS = {
    "btc",
    "bitcoin",
    "ethereum",
    "eth",
    "bnb",
    "sol",
    "solana",
    "dot",
    "link",
    "uni",
    "matic",
    "pol",
    "ada",
    "cardano",
    "xrp",
    "ripple",
    "avax",
    "tron",
    "uni",
    "uniswap",
}
