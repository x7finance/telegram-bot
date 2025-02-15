def get_discounts(chain):
    map = {
        "eth": {
            "eco": {"X7R": 10, "X7DAO": 10, "X7100": 25},
            "liq": {"X7R": 25, "X7DAO": 15, "X7100": 50},
            "dex": "50% LP Fee discounts while trading on Xchange",
            "borrow": "Fee discounts for borrowing funds for ILL on Xchange",
            "magister": {"X7R": 25, "X7100": 25},
        },
        "arb": {
            "eco": {"X7R": 10, "X7DAO": 10, "X7100": 25},
            "liq": {"X7R": 25, "X7DAO": 15, "X7100": 50},
            "dex": "50% LP Fee discounts while trading on Xchange",
            "borrow": "Fee discounts for borrowing funds for ILL on Xchange",
            "magister": {"X7R": 25, "X7100": 25},
        },
        "op": {
            "eco": {"X7R": 10, "X7DAO": 10, "X7100": 25},
            "liq": {"X7R": 25, "X7DAO": 15, "X7100": 50},
            "dex": "50% LP Fee discounts while trading on Xchange",
            "borrow": "Fee discounts for borrowing funds for ILL on Xchange",
            "magister": {"X7R": 25, "X7100": 25},
        },
        "bsc": {
            "eco": {"X7R": 10, "X7DAO": 10, "X7100": 25},
            "liq": {"X7R": 25, "X7DAO": 15, "X7100": 50},
            "dex": "50% LP Fee discounts while trading on Xchange",
            "borrow": "Fee discounts for borrowing funds for ILL on Xchange",
            "magister": {"X7R": 25, "X7100": 25},
        },
        "poly": {
            "eco": {"X7R": 10, "X7DAO": 10, "X7100": 25},
            "liq": {"X7R": 25, "X7DAO": 15, "X7100": 50},
            "dex": "50% LP Fee discounts while trading on Xchange",
            "borrow": "Fee discounts for borrowing funds for ILL on Xchange",
            "magister": {"X7R": 25, "X7100": 25},
        },
        "base": {
            "eco": {"X7R": 10, "X7DAO": 10, "X7100": 25},
            "liq": {"X7R": 25, "X7DAO": 15, "X7100": 50},
            "dex": "50% LP Fee discounts while trading on Xchange",
            "borrow": "Fee discounts for borrowing funds for ILL on Xchange",
            "magister": {"X7R": 25, "X7100": 25},
        },
    }
    return map.get(chain, {})


def get_mint_prices(chain):
    map = {
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
    return map.get(chain, {})


def get_info(chain):
    data = {
        "chain": chain,
        "discounts": get_discounts(chain),
        "mint_prices": get_mint_prices(chain),
    }

    names = {
        "eco": "Ecosystem Maxi",
        "liq": "Liquidity Maxi",
        "dex": "Dex Maxi",
        "borrow": "Borrow Maxi",
        "magister": "Magister",
    }

    output = []

    for key in names:
        display_name = names[key]
        mint_price_text = data["mint_prices"].get(
            key, "Mint Price Not Available"
        )
        discount_info = data["discounts"].get(key, {})
        if isinstance(discount_info, dict):
            discount_text = "\n".join(
                [
                    f"> {value}% discount on {token}"
                    for token, value in discount_info.items()
                ]
            )
        else:
            discount_text = f"> {discount_info}" if discount_info else ""

        output.append(
            f"*{display_name}*\n{mint_price_text}\n{discount_text}\n"
        )

    return "\n".join(output).strip()
