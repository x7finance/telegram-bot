from constants.protocol import addresses
from services import get_blockspan

blockspan = get_blockspan()


def data(chain):
    return {
        "eco": blockspan.get_nft_data(addresses.eco_maxi(chain), chain),
        "liq": blockspan.get_nft_data(addresses.liq_maxi(chain), chain),
        "dex": blockspan.get_nft_data(addresses.dex_maxi(chain), chain),
        "borrow": blockspan.get_nft_data(addresses.borrow_maxi(chain), chain),
        "magister": blockspan.get_nft_data(addresses.magister(chain), chain),
    }


def discounts():
    return {
        "eco": {
            "X7R": 10,
            "X7DAO": 10,
            "X7100": 25,
        },
        "liq": {
            "X7R": 25,
            "X7DAO": 15,
            "X7100": 50,
        },
        "dex": {"50% LP Fee discounts while trading on Xchange"},
        "borrow": {"Fee discounts for borrowing funds for ILL on Xchange"},
        "magister": {
            "X7R": 25,
            "X7100": 25,
        },
    }


def mint_prices(chain):
    prices = {
        "eth": {
            "eco": "Supply - 500\nMint Price - 0.3 ETH",
            "liq": "Supply - 250\nMint Price - 0.75 ETH",
            "dex": "Supply - 150\nMint Price - 1.5 ETH",
            "borrow": "Supply - 100\nMint Price - 2 ETH",
            "magister": "Supply - 49\nMint Price - 50 ETH",
        },
        "arb": {
            "eco": "Supply - 500\nMint Price - 0.3 ETH",
            "liq": "Supply - 250\nMint Price - 0.75 ETH",
            "dex": "Supply - 150\nMint Price - 1.5 ETH",
            "borrow": "Supply - 100\nMint Price - 2 ETH",
            "magister": "Supply - 49\nMint Price - 50 ETH",
        },
        "op": {
            "eco": "Supply - 500\nMint Price - 0.3 ETH",
            "liq": "Supply - 250\nMint Price - 0.75 ETH",
            "dex": "Supply - 150\nMint Price - 1.5 ETH",
            "borrow": "Supply - 100\nMint Price - 2 ETH",
            "magister": "Supply - 49\nMint Price - 50 ETH",
        },
        "bsc": {
            "eco": "Supply - 500\nMint Price - 0.3 ETH",
            "liq": "Supply - 250\nMint Price - 0.75 ETH",
            "dex": "Supply - 150\nMint Price - 1.5 ETH",
            "borrow": "Supply - 100\nMint Price - 2 ETH",
            "magister": "Supply - 49\nMint Price - 50 ETH",
        },
        "poly": {
            "eco": "Supply - 500\nMint Price - 0.3 ETH",
            "liq": "Supply - 250\nMint Price - 0.75 ETH",
            "dex": "Supply - 150\nMint Price - 1.5 ETH",
            "borrow": "Supply - 100\nMint Price - 2 ETH",
            "magister": "Supply - 49\nMint Price - 50 ETH",
        },
        "base": {
            "eco": "Supply - 500\nMint Price - 0.3 ETH",
            "liq": "Supply - 250\nMint Price - 0.75 ETH",
            "dex": "Supply - 150\nMint Price - 1.5 ETH",
            "borrow": "Supply - 100\nMint Price - 2 ETH",
            "magister": "Supply - 49\nMint Price - 50 ETH",
        },
    }
    return prices.get(chain, {})
