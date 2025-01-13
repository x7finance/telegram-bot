from constants import ca, chains, tokens
from hooks import api

dextools = api.Dextools()
etherscan = api.Etherscan()


def generate_eco_split(chain, eth_value):
    if chain in chains.active_chains():
        chain_info, _ = chains.get_info(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(ca.ECO_SPLITTER(chain)),
        abi=etherscan.get_abi(ca.ECO_SPLITTER(chain), chain),
        )
            
    x7r_percentage = contract.functions.outletShare(1).call() / 10
    x7dao_percentage = contract.functions.outletShare(2).call() / 10
    x7100_percentage = contract.functions.outletShare(3).call() / 10
    lending_pool_percentage = contract.functions.outletShare(4).call() / 10
    treasury_percentage = contract.functions.outletShare(5).call() / 10
    
    x7r_balance = contract.functions.outletBalance(1).call() / 10 ** 18
    x7dao_balance = contract.functions.outletBalance(2).call() / 10 ** 18
    x7100_balance = contract.functions.outletBalance(3).call() / 10 ** 18
    lending_pool_balance = contract.functions.outletBalance(4).call() / 10 ** 18
    treasury_balance = contract.functions.outletBalance(5).call() / 10 ** 18

    slot_names = {
        "eth": ("Treasury Splitter"),
        "base": ("X7DAO Multisig"),
        "bsc": (),
        "arb": (),
        "op": (),
        "poly": (),
    }

    treasury_name = (
        slot_names.get(chain) if slot_names.get(chain) else ("Treasury Splitter")
    )

    return {
        "> X7R Liquidity Hub": (x7r_balance, x7r_percentage),
        "> X7DAO Liquidity Hub": (x7dao_balance, x7dao_percentage),
        "> X7100 Liquidity Hub": (x7100_balance, x7100_percentage),
        "> Lending Pool": (lending_pool_balance, lending_pool_percentage),
        f"> {treasury_name}": (treasury_balance, treasury_percentage)
    }
    

def generate_hub_split(chain, hub_address, token):
    if chain in chains.active_chains():
        chain_info, _ = chains.get_info(chain)

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(hub_address), abi=etherscan.get_abi(hub_address, chain)
    )

    distribute, liquidity, treasury, liquidity_ratio_target, balance_threshold = ("N/A",) * 5
    liquidity_balance, distribute_balance, treasury_balance = 0, 0, 0

    try:
        distribute = contract.functions.distributeShare().call() / 10
        liquidity = contract.functions.liquidityShare().call() / 10
        treasury = contract.functions.treasuryShare().call() / 10
        liquidity_ratio_target = contract.functions.liquidityRatioTarget().call() / 10
        balance_threshold = contract.functions.balanceThreshold().call() / 10 ** 18
        liquidity_balance = contract.functions.liquidityBalance().call() / 10 ** 18
        distribute_balance = contract.functions.distributeBalance().call() / 10 ** 18
        treasury_balance = contract.functions.treasuryBalance().call() / 10 ** 18
    except Exception:
        pass

    split = {
        "> Ecosystem Share": f"{distribute:.0f}% - {distribute_balance:,.4f} {chain_info.native.upper()}",
        "> Liquidity Share": f"{liquidity:.0f}% - {liquidity_balance:,.4f} {chain_info.native.upper()}",
        "> Treasury Share": f"{treasury:.0f}% - {treasury_balance:,.4f} {chain_info.native.upper()}",
    }

    threshold_text = f"Balance Threshold: {balance_threshold} {chain_info.native.upper()}"

    token_liquidity_balance = 0
    auxiliary, auxiliary_balance = "N/A", 0
    lending_pool, lending_pool_balance, liquidity_balance_threshold = "N/A", 0, "N/A"

    if token.upper() in tokens.TOKENS:
        token_info = tokens.TOKENS[token.upper()].get(chain)
        address = token_info.ca
        price, _ = dextools.get_price(address, chain)

    if token == "x7r":
        try:
            token_liquidity_balance = contract.functions.x7rLiquidityBalance().call() / 10 ** 18
        except Exception:
            pass

    elif token == "x7dao":
        try:
            token_liquidity_balance = contract.functions.x7daoLiquidityBalance().call() / 10 ** 18
            auxiliary = contract.functions.auxiliaryShare().call() / 10
            auxiliary_balance = contract.functions.auxiliaryBalance().call() / 10 ** 18
            split.update({
                "> Auxiliary Share": f"{auxiliary:.0f}% - {auxiliary_balance:,.4f} {chain_info.native.upper()}",
            })
        except Exception:
            pass

    elif token in ["x7101", "x7102", "x7103", "x7104", "x7105"]:
        try:
            token_liquidity_balance = contract.functions.liquidityTokenBalance(address).call() / 10 ** 18
            lending_pool = contract.functions.lendingPoolShare().call() / 10
            lending_pool_balance = contract.functions.lendingPoolBalance().call() / 10 ** 18
            liquidity_balance_threshold = contract.functions.liquidityBalanceThreshold().call() / 10 ** 18
            split.update({
                "> Lending Pool Share": f"{lending_pool:.0f}% - {lending_pool_balance:,.4f} {chain_info.native.upper()}",
            })
            threshold_text += f"\nLiquidity Balance Threshold: {liquidity_balance_threshold} {chain_info.native.upper()}"
        except Exception:
            pass

    balance = (float(etherscan.get_token_balance(hub_address, address, chain)) / 10 ** 18)  - float(token_liquidity_balance)
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


def generate_treasury_split(chain, eth_value):
    if chain in chains.active_chains():
        chain_info, _ = chains.get_info(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(ca.TREASURY_SPLITTER(chain)),
        abi=etherscan.get_abi(ca.TREASURY_SPLITTER(chain), chain),
    )
    
    profit_percentage = contract.functions.outletShare(1).call() / 1000
    reward_pool_percentage = contract.functions.outletShare(2).call() / 1000
    slot_1_percentage = contract.functions.outletShare(3).call() / 1000
    slot_2_percentage = contract.functions.outletShare(4).call() / 1000

    profit_balance = contract.functions.outletBalance(1).call() / 10 ** 18
    reward_pool_balance = contract.functions.outletBalance(2).call() / 10 ** 18
    slot_1_balance = contract.functions.outletBalance(3).call() / 10 ** 18
    slot_2_balance = contract.functions.outletBalance(4).call() / 10 ** 18

    profit_balance = eth_value * profit_percentage / 100
    reward_pool_balance = eth_value * reward_pool_percentage / 100
    slot_1_balance = eth_value * slot_1_percentage / 100
    slot_2_balance = eth_value * slot_2_percentage / 100

    slot_names = {
        "eth": ("Pioneer Pool", "Community Multi Sig", "Utility Deployer"),
        "base": (),
        "bsc": (),
        "arb": (),
        "op": (),
        "poly": (),
    }

    rewards_pool_name, slot_1_name, slot_2_name = (
        slot_names.get(chain) if slot_names.get(chain) else ("Rewards Pool", "Slot 1", "Slot 2")
    )

    return {
            "> DAO Multi Sig": (profit_balance, profit_percentage), 
            f"> {rewards_pool_name}": (reward_pool_balance, reward_pool_percentage),
            f"> {slot_1_name}": (slot_1_balance, slot_1_percentage),
            f"> {slot_2_name}": (slot_2_balance, slot_2_percentage)
    }


def get_push_settings(chain): 
    return {
        "push_eco": {
            "splitter_address": ca.ECO_SPLITTER(chain),
            "splitter_name": "Ecosystem Splitter",
            "threshold": 0.01 if chain.lower() == "eth" else 0.0001,
            "contract_type": "splitter",
            "balance_func": lambda contract: contract.functions.outletBalance(4).call() / 10 ** 18
        },
        "push_treasury": {
            "splitter_address": ca.TREASURY_SPLITTER(chain),
            "splitter_name": "Treasury Splitter",
            "threshold": 0.01 if chain.lower() == "eth" else 0.0001,
            "contract_type": "splitter",
            "balance_func": lambda _: etherscan.get_native_balance(ca.TREASURY_SPLITTER(chain), chain)
        },
        "push_x7r": {
            "splitter_address": ca.X7R_LIQ_HUB(chain),
            "splitter_name": "X7R Liquidity Hub",
            "token_address": ca.X7R(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda contract: float(etherscan.get_token_balance(
                ca.X7R_LIQ_HUB(chain), ca.X7R(chain), chain)
                ) - contract.functions.x7rLiquidityBalance().call()
        },
        "push_x7dao": {
            "splitter_address": ca.X7DAO_LIQ_HUB(chain),
            "splitter_name": "X7DAO Liquidity Hub",
            "token_address": ca.X7DAO(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda contract: float(etherscan.get_token_balance(
                ca.X7DAO_LIQ_HUB(chain), ca.X7DAO(chain), chain)
                ) - contract.functions.x7daoLiquidityBalance().call()
        },
        "push_x7101": {
            "splitter_address": ca.X7100_LIQ_HUB(chain),
            "splitter_name": "X7100 Liquidity Hub",
            "token_address": ca.X7101(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda _: etherscan.get_token_balance(ca.X7100_LIQ_HUB(chain), ca.X7101(chain), chain)
        },
        "push_x7102": {
            "splitter_address": ca.X7100_LIQ_HUB(chain),
            "splitter_name": "X7100 Liquidity Hub",
            "token_address": ca.X7102(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda _: etherscan.get_token_balance(ca.X7100_LIQ_HUB(chain), ca.X7102(chain), chain)
        },
        "push_x7103": {
            "splitter_address": ca.X7100_LIQ_HUB(chain),
            "splitter_name": "X7100 Liquidity Hub",
            "token_address": ca.X7103(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda _: etherscan.get_token_balance(ca.X7100_LIQ_HUB(chain), ca.X7103(chain), chain)
        },
        "push_x7104": {
            "splitter_address": ca.X7100_LIQ_HUB(chain),
            "splitter_name": "X7100 Liquidity Hub",
            "token_address": ca.X7104(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda _: etherscan.get_token_balance(ca.X7100_LIQ_HUB(chain), ca.X7104(chain), chain)
        },
        "push_x7105": {
            "splitter_address": ca.X7100_LIQ_HUB(chain),
            "splitter_name": "X7100 Liquidity Hub",
            "token_address": ca.X7105(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda _: etherscan.get_token_balance(ca.X7100_LIQ_HUB(chain), ca.X7105(chain), chain)
        },
    }