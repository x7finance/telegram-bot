from constants import abis, ca, chains, tokens
from hooks import api

dextools = api.Dextools()
etherscan = api.Etherscan()


def generate_eco_split(chain):
    if chain in chains.active_chains():
        chain_info, _ = chains.get_info(chain)

    address = ca.ECO_SPLITTER(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address),
        abi=abis.read("ecosystemsplitter"),
    )

    x7r_percentage = contract.functions.outletShare(1).call() / 10
    x7dao_percentage = contract.functions.outletShare(2).call() / 10
    x7100_percentage = contract.functions.outletShare(3).call() / 10
    lending_pool_percentage = contract.functions.outletShare(4).call() / 10
    treasury_percentage = contract.functions.outletShare(5).call() / 10

    x7r_balance = contract.functions.outletBalance(1).call() / 10**18
    x7dao_balance = contract.functions.outletBalance(2).call() / 10**18
    x7100_balance = contract.functions.outletBalance(3).call() / 10**18
    lending_pool_balance = contract.functions.outletBalance(4).call() / 10**18
    treasury_balance = contract.functions.outletBalance(5).call() / 10**18

    slot_names = {
        "eth": ("Treasury Splitter"),
        "base": ("X7DAO Multisig"),
        "bsc": (),
        "arb": (),
        "op": (),
        "poly": (),
    }

    treasury_name = (
        slot_names.get(chain)
        if slot_names.get(chain)
        else ("Treasury Splitter")
    )

    return {
        "> X7R Liquidity Hub": (x7r_balance, x7r_percentage),
        "> X7DAO Liquidity Hub": (x7dao_balance, x7dao_percentage),
        "> X7100 Liquidity Hub": (x7100_balance, x7100_percentage),
        "> Lending Pool": (lending_pool_balance, lending_pool_percentage),
        f"> {treasury_name}": (treasury_balance, treasury_percentage),
    }


def generate_hub_split(chain, address, token):
    if chain in chains.active_chains():
        chain_info, _ = chains.get_info(chain)

    abi = get_push_settings(chain)[token]["abi"]

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address), abi=abi
    )

    (
        distribute,
        liquidity,
        treasury,
        liquidity_ratio_target,
        balance_threshold,
    ) = ("N/A",) * 5
    liquidity_balance, distribute_balance, treasury_balance = 0, 0, 0

    try:
        distribute = contract.functions.distributeShare().call() / 10
        liquidity = contract.functions.liquidityShare().call() / 10
        treasury = contract.functions.treasuryShare().call() / 10
        liquidity_ratio_target = (
            contract.functions.liquidityRatioTarget().call() / 10
        )
        balance_threshold = (
            contract.functions.balanceThreshold().call() / 10**18
        )
        liquidity_balance = (
            contract.functions.liquidityBalance().call() / 10**18
        )
        distribute_balance = (
            contract.functions.distributeBalance().call() / 10**18
        )
        treasury_balance = contract.functions.treasuryBalance().call() / 10**18
    except Exception:
        pass

    split = {
        "> Ecosystem Share": f"{distribute:.0f}% - {distribute_balance:,.4f} {chain_info.native.upper()}",
        "> Liquidity Share": f"{liquidity:.0f}% - {liquidity_balance:,.4f} {chain_info.native.upper()}",
        "> Treasury Share": f"{treasury:.0f}% - {treasury_balance:,.4f} {chain_info.native.upper()}",
    }

    threshold_text = (
        f"Balance Threshold: {balance_threshold} {chain_info.native.upper()}"
    )

    token_liquidity_balance = 0
    auxiliary, auxiliary_balance = "N/A", 0
    lending_pool, lending_pool_balance, liquidity_balance_threshold = (
        "N/A",
        0,
        "N/A",
    )

    if token.upper() in tokens.get_tokens():
        token_info = tokens.get_tokens()[token.upper()].get(chain)
        price, _ = dextools.get_price(token_info.ca, chain)

    if token == "x7r":
        try:
            token_liquidity_balance = (
                contract.functions.x7rLiquidityBalance().call() / 10**18
            )
        except Exception:
            pass

    elif token == "x7dao":
        try:
            token_liquidity_balance = (
                contract.functions.x7daoLiquidityBalance().call() / 10**18
            )
            auxiliary = contract.functions.auxiliaryShare().call() / 10
            auxiliary_balance = (
                contract.functions.auxiliaryBalance().call() / 10**18
            )
            split.update(
                {
                    "> Auxiliary Share": f"{auxiliary:.0f}% - {auxiliary_balance:,.4f} {chain_info.native.upper()}",
                }
            )
        except Exception:
            pass

    elif token in ["x7101", "x7102", "x7103", "x7104", "x7105"]:
        try:
            token_liquidity_balance = (
                contract.functions.liquidityTokenBalance(token_info.ca).call()
                / 10**18
            )
            lending_pool = contract.functions.lendingPoolShare().call() / 10
            lending_pool_balance = (
                contract.functions.lendingPoolBalance().call() / 10**18
            )
            liquidity_balance_threshold = (
                contract.functions.liquidityBalanceThreshold().call() / 10**18
            )
            split.update(
                {
                    "> Lending Pool Share": f"{lending_pool:.0f}% - {lending_pool_balance:,.4f} {chain_info.native.upper()}",
                }
            )
            threshold_text += f"\nLiquidity Balance Threshold: {liquidity_balance_threshold} {chain_info.native.upper()}"
        except Exception:
            pass

    balance = (
        float(etherscan.get_token_balance(address, token_info.ca, chain))
        / 10**18
    ) - float(token_liquidity_balance)
    balance_dollar = float(price) * float(balance)
    balance_text = f"{balance:,.0f} {token.upper()} (${balance_dollar:,.0f})"

    split_text = "\n".join([f"{key}: {value}" for key, value in split.items()])

    return (
        f"{balance_text}\n\n"
        f"{threshold_text}\n\n"
        f"{split_text}\n\n"
        f"Liquidity Ratio Target: {liquidity_ratio_target}%\n"
        f"Reserved Token Liquidity: {token_liquidity_balance:,.0f} {token.upper()}"
    )


def generate_treasury_split(chain):
    if chain in chains.active_chains():
        chain_info, _ = chains.get_info(chain)

    address = ca.TREASURY_SPLITTER(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address),
        abi=abis.read("treasurysplitter"),
    )

    profit_percentage = contract.functions.outletShare(1).call() / 1000
    reward_pool_percentage = contract.functions.outletShare(2).call() / 1000
    slot_1_percentage = contract.functions.outletShare(3).call() / 1000
    slot_2_percentage = contract.functions.outletShare(4).call() / 1000

    profit_balance = contract.functions.outletBalance(1).call() / 10**18
    reward_pool_balance = contract.functions.outletBalance(2).call() / 10**18
    slot_1_balance = contract.functions.outletBalance(3).call() / 10**18
    slot_2_balance = contract.functions.outletBalance(4).call() / 10**18

    slot_names = {
        "eth": ("Pioneer Pool", "Community Multi Sig", "Utility Deployer"),
        "base": (),
        "bsc": (),
        "arb": (),
        "op": (),
        "poly": (),
    }

    rewards_pool_name, slot_1_name, slot_2_name = (
        slot_names.get(chain)
        if slot_names.get(chain)
        else ("Rewards Pool", "Slot 1", "Slot 2")
    )

    return {
        "> DAO Multi Sig": (profit_balance, profit_percentage),
        f"> {rewards_pool_name}": (
            reward_pool_balance,
            reward_pool_percentage,
        ),
        f"> {slot_1_name}": (slot_1_balance, slot_1_percentage),
        f"> {slot_2_name}": (slot_2_balance, slot_2_percentage),
    }


def get_push_settings(chain):
    return {
        "eco": {
            "address": ca.ECO_SPLITTER(chain),
            "abi": abis.read("ecosystemsplitter"),
            "name": "Ecosystem Splitter",
            "threshold": 0.01 if chain.lower() == "eth" else 0.0001,
            "contract_type": "splitter",
            "calculate_tokens": lambda contract: contract.functions.outletBalance(
                4
            ).call()
            / 10**18,
            "recipient": ca.LPOOL_RESERVE(chain),
        },
        "treasury": {
            "address": ca.TREASURY_SPLITTER(chain),
            "abi": abis.read("treasurysplitter"),
            "name": "Treasury Splitter",
            "threshold": 0.01 if chain.lower() == "eth" else 0.0001,
            "contract_type": "splitter",
            "calculate_tokens": lambda _: etherscan.get_native_balance(
                ca.TREASURY_SPLITTER(chain), chain
            ),
            "recipient": ca.DAO_MULTI(chain),
        },
        "x7r": {
            "address": ca.X7R_LIQ_HUB(chain),
            "abi": abis.read("x7rliquidityhub"),
            "name": "X7R Liquidity Hub",
            "token_address": ca.X7R(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda contract: float(
                etherscan.get_token_balance(
                    ca.X7R_LIQ_HUB(chain), ca.X7R(chain), chain
                )
            )
            - contract.functions.x7rLiquidityBalance().call(),
        },
        "x7dao": {
            "address": ca.X7DAO_LIQ_HUB(chain),
            "abi": abis.read("x7daoliquidityhub"),
            "name": "X7DAO Liquidity Hub",
            "token_address": ca.X7DAO(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda contract: float(
                etherscan.get_token_balance(
                    ca.X7DAO_LIQ_HUB(chain), ca.X7DAO(chain), chain
                )
            )
            - contract.functions.x7daoLiquidityBalance().call(),
        },
        "x7101": {
            "address": ca.X7100_LIQ_HUB(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": ca.X7101(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda _: etherscan.get_token_balance(
                ca.X7100_LIQ_HUB(chain), ca.X7101(chain), chain
            ),
        },
        "x7102": {
            "address": ca.X7100_LIQ_HUB(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": ca.X7102(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda _: etherscan.get_token_balance(
                ca.X7100_LIQ_HUB(chain), ca.X7102(chain), chain
            ),
        },
        "x7103": {
            "address": ca.X7100_LIQ_HUB(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": ca.X7103(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda _: etherscan.get_token_balance(
                ca.X7100_LIQ_HUB(chain), ca.X7103(chain), chain
            ),
        },
        "x7104": {
            "address": ca.X7100_LIQ_HUB(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": ca.X7104(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda _: etherscan.get_token_balance(
                ca.X7100_LIQ_HUB(chain), ca.X7104(chain), chain
            ),
        },
        "x7105": {
            "address": ca.X7100_LIQ_HUB(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": ca.X7105(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda _: etherscan.get_token_balance(
                ca.X7100_LIQ_HUB(chain), ca.X7105(chain), chain
            ),
        },
    }
