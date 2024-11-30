from constants import ca, chains
from typing import Union


class TokensInfo:
    def __init__(
        self,
        name: str,
        ca: str,
        pairs: Union[str, list]
    ):
        self.name = name
        self.ca = ca
        self.pairs = pairs


TOKENS = {
    "X7DAO": {chain: TokensInfo("X7DAO", ca.X7DAO(chain), ca.X7DAO_PAIR(chain)) for chain in chains.active_chains()},
    "X7R": {chain: TokensInfo("X7R", ca.X7R(chain), ca.X7R_PAIR(chain)) for chain in chains.active_chains()},
    "X7101": {chain: TokensInfo("X7101", ca.X7101(chain), ca.X7101_PAIR(chain)) for chain in chains.active_chains()},
    "X7102": {chain: TokensInfo("X7102", ca.X7102(chain), ca.X7102_PAIR(chain)) for chain in chains.active_chains()},
    "X7103": {chain: TokensInfo("X7103", ca.X7103(chain), ca.X7103_PAIR(chain)) for chain in chains.active_chains()},
    "X7104": {chain: TokensInfo("X7104", ca.X7104(chain), ca.X7104_PAIR(chain)) for chain in chains.active_chains()},
    "X7105": {chain: TokensInfo("X7105", ca.X7105(chain), ca.X7105_PAIR(chain)) for chain in chains.active_chains()}
}

BLUE_CHIPS = ["btc", "bitcoin", "ethereum", "eth", "bnb", "sol", "solana", "dot", "link", "uni", "matic", "pol", "ada", "cardano", "xrp", "ripple", "avax", "tron", "uni", "uniswap"]
