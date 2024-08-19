# TOKENS

from constants import ca


class TokensInfo:
    def __init__(
        self,
        ca: str,
        pair: str
    ):
        self.ca = ca
        self.pair = pair


def TOKENS(chain):
    return {
    "X7DAO": {
        "eth": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR(chain)
        ),
        "arb": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR(chain)
        ),
        "poly": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR(chain)
        ),
        "bsc": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR(chain)
        ),
        "op": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR(chain)
        ),
        "base": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR(chain)
        ),
    },
    "X7R": {
        "eth": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR(chain)
        ),
        "arb": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR(chain)
        ),
        "poly": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR(chain)
        ),
        "bsc": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR(chain)
        ),
        "op": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR(chain)
        ),
        "base": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR(chain)
        ),
    },
    "X7101": {
        "eth": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR(chain)
        ),
        "arb": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR(chain)
        ),
        "poly": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR(chain)
        ),
        "bsc": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR(chain)
        ),
        "op": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR(chain)
        ),
        "base": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR(chain)
        ),
    },
    "X7102": {
        "eth": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR(chain)
        ),
        "arb": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR(chain)
        ),
        "poly": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR(chain)
        ),
        "bsc": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR(chain)
        ),
        "op": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR(chain)
        ),
        "base": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR(chain)
        ),
    },

    "X7103": {
        "eth": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR(chain)
        ),
        "arb": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR(chain)
        ),
        "poly": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR(chain)
        ),
        "bsc": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR(chain)
        ),
        "op": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR(chain)
        ),
        "base": TokensInfo(
            ca.X7103(chain),
         ca.X7103_PAIR(chain)
        ),
    },
    "X7104": {
        "eth": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR(chain)
        ),
        "arb": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR(chain)
        ),
        "poly": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR(chain)
        ),
        "bsc": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR(chain)
        ),
        "op": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR(chain)
        ),
        "base": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR(chain)
        ),
    },
    "X7105": {
        "eth": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR(chain)
        ),
        "arb": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR(chain)
        ),
        "poly": TokensInfo(
            ca.X7105(chain), 
            ca.X7105_PAIR(chain)
        ),
        "bsc": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR(chain)
        ),
        "op": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR(chain)
        ),
        "base": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR(chain)
        ),
    },
}
