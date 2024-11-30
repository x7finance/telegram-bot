SWAP_GAS = 356190

INFO = {
    "eth": {
        "x7r": 3,
        "x7dao": 3,
        "x7100": 2,
    },
    "op": {
        "x7r": 6,
        "x7dao": 6,
        "x7100": 2,
    },
    "poly": {
        "x7r": 6,
        "x7dao": 6,
        "x7100": 2,
    },
    "arb": {
        "x7r": 6,
        "x7dao": 6,
        "x7100": 2,
    },
    "bsc": {
        "x7r": 6,
        "x7dao": 6,
        "x7100": 2,
    },
    "base": {
        "x7r": 6,
        "x7dao": 6,
        "x7100": 2,
    },
}


DISCOUNTS = {
    "x7dao_discount_x7100": 50,
    "liq_discount_x7r": 25,
    "liq_discount_x7dao": 15,
    "liq_discount_x7100": 50,
    "eco_discount_x7r": 10,
    "eco_discount_x7dao": 10,
    "eco_discount_x7100": 25,
    "magister_discount": 25,
}


def generate_info(chain):
    chain_info = INFO.get(chain)
    if chain_info:
        x7r = chain_info["x7r"]
        x7dao = chain_info["x7dao"]
        x7100 = chain_info["x7100"]

        x7dao_discount_x7100 = DISCOUNTS["x7dao_discount_x7100"]
        liq_discount_x7r = DISCOUNTS["liq_discount_x7r"]
        liq_discount_x7dao = DISCOUNTS["liq_discount_x7dao"]
        liq_discount_x7100 = DISCOUNTS["liq_discount_x7100"]
        eco_discount_x7r = DISCOUNTS["eco_discount_x7r"]
        eco_discount_x7dao = DISCOUNTS["eco_discount_x7dao"]
        eco_discount_x7100 = DISCOUNTS["eco_discount_x7100"]
        magister_discount = DISCOUNTS["magister_discount"]

        chain_info_str = (
            f"X7R: {x7r}%\nX7DAO: {x7dao}%\n"
            f"X7101-X7105: {x7100}%\n\n"
            "*Tax with Discounts*\n\n"
            "50000 X7DAO:\n"
            f"X7R: {x7r}%\n"
            f"X7DAO: {x7dao}%\n"
            f"X7101 - X7105: {x7100 - (x7100 * x7dao_discount_x7100 / 100)}%\n\n"
            "Ecosystem Maxi:\n"
            f"X7R: {x7r - (x7r * eco_discount_x7r / 100)}%\n"
            f"X7DAO: {x7dao - (x7dao * eco_discount_x7dao / 100)}%\n"
            f"X7101-X7105: {x7100 - (x7100 * eco_discount_x7100 / 100)}%\n\n"
            "Liquidity Maxi:\n"
            f"X7R: {x7r - (x7r * liq_discount_x7r / 100)}%\n"
            f"X7DAO: {x7dao - (x7dao * liq_discount_x7dao / 100)}%\n"
            f"X7101-X7105: {x7100 - (x7100 * liq_discount_x7100 / 100)}%\n\n"
            "Magister:\n"
            f"X7R: {x7r - (x7r * magister_discount / 100)}%\n"
            f"X7DAO: {x7dao}%\n"
            f"X7101-X7105: {x7100 - (x7100 * magister_discount / 100)}%\n"
        )

        return chain_info_str
