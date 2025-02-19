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
                name="X7DAO",
                ca=addresses.x7dao(chain),
                pairs=addresses.x7dao_pair(chain),
                hub=addresses.x7dao_liquidity_hub(chain),
                logo=token_logos.X7DAO_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7r": {
            chain: TokensInfo(
                name="X7R",
                ca=addresses.x7r(chain),
                pairs=addresses.x7r_pair(chain),
                hub=addresses.x7r_liquidity_hub(chain),
                logo=token_logos.X7R_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7101": {
            chain: TokensInfo(
                name="X7101",
                ca=addresses.x7101(chain),
                pairs=addresses.x7101_pair(chain),
                hub=addresses.x7100_liquidity_hub(chain),
                logo=token_logos.X7101_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7102": {
            chain: TokensInfo(
                name="X7102",
                ca=addresses.x7102(chain),
                pairs=addresses.x7102_pair(chain),
                hub=addresses.x7100_liquidity_hub(chain),
                logo=token_logos.X7102_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7103": {
            chain: TokensInfo(
                name="X7103",
                ca=addresses.x7103(chain),
                pairs=addresses.x7103_pair(chain),
                hub=addresses.x7100_liquidity_hub(chain),
                logo=token_logos.X7103_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7104": {
            chain: TokensInfo(
                name="X7104",
                ca=addresses.x7104(chain),
                pairs=addresses.x7104_pair(chain),
                hub=addresses.x7100_liquidity_hub(chain),
                logo=token_logos.X7104_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7105": {
            chain: TokensInfo(
                name="X7105",
                ca=addresses.x7105(chain),
                pairs=addresses.x7105_pair(chain),
                hub=addresses.x7100_liquidity_hub(chain),
                logo=token_logos.X7105_LOGO,
            )
            for chain in chains.get_active_chains()
        },
        "x7D": {
            chain: TokensInfo(
                name="X7D",
                ca=addresses.x7d(chain),
                pairs=None,
                hub=None,
                logo=token_logos.X7D_LOGO,
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
