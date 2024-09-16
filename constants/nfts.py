# NFTS

from constants import ca
from hooks import api


def data(chain):
    return {
        "eco": api.get_nft_data(ca.ECO(chain), chain),
        "liq": api.get_nft_data(ca.LIQ(chain), chain),
        "dex": api.get_nft_data(ca.DEX(chain), chain),
        "borrow": api.get_nft_data(ca.BORROW(chain), chain),
        "magister": api.get_nft_data(ca.MAGISTER(chain), chain),
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
            "eco": "0.3 ETH - 500 Supply",
            "liq": "0.75 ETH - 250 Supply",
            "dex": "1.5 ETH - 150 Supply",
            "borrow": "2 ETH - 100 Supply",
            "magister": "50 ETH - 49 Supply",
        },
        "arb": {
            "eco": "0.3 ETH - 500 Supply",
            "liq": "0.75 ETH - 250 Supply",
            "dex": "1.5 ETH - 150 Supply",
            "borrow": "2 ETH - 100 Supply",
            "magister": "50 ETH - 49 Supply",
        },
        "op": {
            "eco": "0.3 ETH - 500 Supply",
            "liq": "0.75 ETH - 250 Supply",
            "dex": "1.5 ETH - 150 Supply",
            "borrow": "2 ETH - 100 Supply",
            "magister": "50 ETH - 49 Supply",
        },
        "bsc": {
            "eco": "1.5 BNB - 500 Supply",
            "liq": "3.75 BNB - 250 Supply",
            "dex": "7.5 BNB - 150 Supply",
            "borrow": "10 BNB - 100 Supply",
            "magister": "150 BNB - 49 Supply",
        },
        "poly": {
            "eco": "390 MATIC - 500 Supply",
            "liq": "975 MATIC - 250 Supply",
            "dex": "1950 MATIC - 150 Supply",
            "borrow": "2600 MATIC - 100 Supply",
            "magister": "45000 MATIC - 49 Supply",
        },
        "base": {
            "eco": "0.3 ETH - 500 Supply",
            "liq": "0.75 ETH - 250 Supply",
            "dex": "1.5 ETH - 150 Supply",
            "borrow": "2 ETH - 100 Supply",
            "magister": "50 ETH - 49 Supply",
        },
    }
    return prices.get(chain, {})

