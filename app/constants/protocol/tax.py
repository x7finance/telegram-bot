SWAP_GAS = 356190


def get_tax(chain):
    map = {
        "eth": {"x7r": 3, "x7dao": 3, "x7100": 2},
        "op": {"x7r": 6, "x7dao": 6, "x7100": 2},
        "poly": {"x7r": 6, "x7dao": 6, "x7100": 2},
        "arb": {"x7r": 6, "x7dao": 6, "x7100": 2},
        "bsc": {"x7r": 6, "x7dao": 6, "x7100": 2},
        "base": {"x7r": 6, "x7dao": 6, "x7100": 2},
    }

    return map.get(chain.lower(), {})


def get_discounts(chain):
    map = {
        "eth": {
            "x7dao_discount_x7100": 50,
            "liq_discount_x7r": 25,
            "liq_discount_x7dao": 15,
            "liq_discount_x7100": 50,
            "eco_discount_x7r": 10,
            "eco_discount_x7dao": 10,
            "eco_discount_x7100": 25,
            "magister_discount": 25,
        },
        "op": {
            "x7dao_discount_x7100": 50,
            "liq_discount_x7r": 25,
            "liq_discount_x7dao": 15,
            "liq_discount_x7100": 50,
            "eco_discount_x7r": 10,
            "eco_discount_x7dao": 10,
            "eco_discount_x7100": 25,
            "magister_discount": 25,
        },
        "poly": {
            "x7dao_discount_x7100": 50,
            "liq_discount_x7r": 25,
            "liq_discount_x7dao": 15,
            "liq_discount_x7100": 50,
            "eco_discount_x7r": 10,
            "eco_discount_x7dao": 10,
            "eco_discount_x7100": 25,
            "magister_discount": 25,
        },
        "arb": {
            "x7dao_discount_x7100": 50,
            "liq_discount_x7r": 25,
            "liq_discount_x7dao": 15,
            "liq_discount_x7100": 50,
            "eco_discount_x7r": 10,
            "eco_discount_x7dao": 10,
            "eco_discount_x7100": 25,
            "magister_discount": 25,
        },
        "bsc": {
            "x7dao_discount_x7100": 50,
            "liq_discount_x7r": 25,
            "liq_discount_x7dao": 15,
            "liq_discount_x7100": 50,
            "eco_discount_x7r": 10,
            "eco_discount_x7dao": 10,
            "eco_discount_x7100": 25,
            "magister_discount": 25,
        },
        "base": {
            "x7dao_discount_x7100": 50,
            "liq_discount_x7r": 25,
            "liq_discount_x7dao": 15,
            "liq_discount_x7100": 50,
            "eco_discount_x7r": 10,
            "eco_discount_x7dao": 10,
            "eco_discount_x7100": 25,
            "magister_discount": 25,
        },
    }

    return map.get(chain.lower(), {})


def get_info(chain):
    tax = get_tax(chain)
    discounts = get_discounts(chain)

    x7r = tax.get("x7r", 0)
    x7dao = tax.get("x7dao", 0)
    x7100 = tax.get("x7100", 0)

    x7dao_discount_x7100 = discounts.get("x7dao_discount_x7100", 0)
    liq_discount_x7r = discounts.get("liq_discount_x7r", 0)
    liq_discount_x7dao = discounts.get("liq_discount_x7dao", 0)
    liq_discount_x7100 = discounts.get("liq_discount_x7100", 0)
    eco_discount_x7r = discounts.get("eco_discount_x7r", 0)
    eco_discount_x7dao = discounts.get("eco_discount_x7dao", 0)
    eco_discount_x7100 = discounts.get("eco_discount_x7100", 0)
    magister_discount = discounts.get("magister_discount", 0)

    chain_info_str = (
        f"X7R: {x7r}%\nX7DAO: {x7dao}%\n"
        f"X7101-X7105: {x7100}%\n\n"
        "*Tax with Discounts*\n\n"
        "50000 X7DAO:\n"
        f"X7R: {x7r}%\n"
        f"X7DAO: {x7dao}%\n"
        f"X7101 - X7105: {x7100 - (x7100 * x7dao_discount_x7100 / 100):.2f}%\n\n"
        "Ecosystem Maxi:\n"
        f"X7R: {x7r - (x7r * eco_discount_x7r / 100):.2f}%\n"
        f"X7DAO: {x7dao - (x7dao * eco_discount_x7dao / 100):.2f}%\n"
        f"X7101-X7105: {x7100 - (x7100 * eco_discount_x7100 / 100):.2f}%\n\n"
        "Liquidity Maxi:\n"
        f"X7R: {x7r - (x7r * liq_discount_x7r / 100):.2f}%\n"
        f"X7DAO: {x7dao - (x7dao * liq_discount_x7dao / 100):.2f}%\n"
        f"X7101-X7105: {x7100 - (x7100 * liq_discount_x7100 / 100):.2f}%\n\n"
        "Magister:\n"
        f"X7R: {x7r - (x7r * magister_discount / 100):.2f}%\n"
        f"X7DAO: {x7dao}%\n"
        f"X7101-X7105: {x7100 - (x7100 * magister_discount / 100):.2f}%\n"
    )

    return chain_info_str
