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
            ca.X7DAO_PAIR_ETH
        ),
        "arb": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR_ARB
        ),
        "poly": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR_POLY
        ),
        "bsc": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR_BSC
        ),
        "op": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR_OP
        ),
        "base": TokensInfo(
            ca.X7DAO(chain),
            ca.X7DAO_PAIR_BASE
        ),
    },
    "X7R": {
        "eth": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR_ETH
        ),
        "arb": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR_ARB
        ),
        "poly": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR_POLY
        ),
        "bsc": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR_BSC
        ),
        "op": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR_OP
        ),
        "base": TokensInfo(
            ca.X7R(chain),
            ca.X7R_PAIR_BASE
        ),
    },
    "X7101": {
        "eth": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR_ETH
        ),
        "arb": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR_ARB
        ),
        "poly": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR_POLY
        ),
        "bsc": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR_BSC
        ),
        "op": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR_OP
        ),
        "base": TokensInfo(
            ca.X7101(chain),
            ca.X7101_PAIR_BASE
        ),
    },
    "X7102": {
        "eth": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR_ETH
        ),
        "arb": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR_ARB
        ),
        "poly": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR_POLY
        ),
        "bsc": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR_BSC
        ),
        "op": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR_OP
        ),
        "base": TokensInfo(
            ca.X7102(chain),
            ca.X7102_PAIR_BASE
        ),
    },

    "X7103": {
        "eth": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR_ETH
        ),
        "arb": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR_ARB
        ),
        "poly": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR_POLY
        ),
        "bsc": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR_BSC
        ),
        "op": TokensInfo(
            ca.X7103(chain),
            ca.X7103_PAIR_OP
        ),
        "base": TokensInfo(
            ca.X7103(chain),
         ca.X7103_PAIR_BASE
        ),
    },
    "X7104": {
        "eth": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR_ETH
        ),
        "arb": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR_ARB
        ),
        "poly": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR_POLY
        ),
        "bsc": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR_BSC
        ),
        "op": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR_OP
        ),
        "base": TokensInfo(
            ca.X7104(chain),
            ca.X7104_PAIR_BASE
        ),
    },
    "X7105": {
        "eth": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR_ETH
        ),
        "arb": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR_ARB
        ),
        "poly": TokensInfo(
            ca.X7105(chain), 
            ca.X7105_PAIR_POLY
        ),
        "bsc": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR_BSC
        ),
        "op": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR_OP
        ),
        "base": TokensInfo(
            ca.X7105(chain),
            ca.X7105_PAIR_BASE
        ),
    },
}
