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
        distribute = "N/A"
        liquidity = "N/A"
        treasury = "N/A"
        liquidity_ratio_target = "N/A"
        balance_threshold = "N/A"
        liquidity_balance = 0
        distribute_balance = 0
        treasury_balance = 0

    split_text = (
        f"Ecosystem Share: {distribute:.0f}% - {distribute_balance:,.3f} {chain_info.native.upper()}\n"
        f"Liquidity Share: {liquidity:.0f}% - {liquidity_balance:,.3f} {chain_info.native.upper()}\n"
        f"Treasury Share: {treasury:.0f}% - {treasury_balance:,.3f} {chain_info.native.upper()}"
    )

    threshold_text = f"Balance Threshold: {balance_threshold} {chain_info.native.upper()}"
    
    balance = 0
    if token.upper() in tokens.TOKENS:
        token_info = tokens.TOKENS[token.upper()].get(chain)
        address = token_info.ca
        price, _ = dextools.get_price(address, chain)

    if token == "x7r":
        try:
            token_liquidity_balance = contract.functions.x7rLiquidityBalance().call() / 10 ** 18
        except Exception:
            token_liquidity_balance = 0
            
    if token == "x7dao":
        try:
            token_liquidity_balance = contract.functions.x7daoLiquidityBalance().call() / 10 ** 18
            auxiliary = contract.functions.auxiliaryShare().call() / 10
            auxiliary_balance = contract.functions.auxiliaryBalance().call() / 10 ** 18
        except Exception:
            token_liquidity_balance = 0
            auxiliary = "N/A"
            auxiliary_balance = 0
        split_text += f"\nAuxiliary Share: {auxiliary:,.0f}% - {auxiliary_balance:,.3f} {chain_info.native.upper()}"

    if token in ["x7101", "x7102", "x7103","x7104","x7105"]:
        token_info = tokens.TOKENS.get(token.upper(), {}).get(chain)
        try:
            token_liquidity_balance = contract.functions.liquidityTokenBalance(address).call() / 10 ** 18
            lending_pool = contract.functions.lendingPoolShare().call() / 10
            lending_pool_balance = contract.functions.lendingPoolBalance().call() / 10 ** 18
            liquidity_balance_threshold = contract.functions.liquidityBalanceThreshold().call() / 10 ** 18
        except Exception as e:
            token_liquidity_balance = 0
            lending_pool = "N/A"
            lending_pool_balance = 0
            liquidity_balance_threshold = "N/A"
        split_text += f"\nLending Pool Share: {lending_pool:,.0f}% - {lending_pool_balance:,.3f} {chain_info.native.upper()}"
        threshold_text += f"\nLiquidity Balance Threshold: {liquidity_balance_threshold} {chain_info.native.upper()}"
    
    balance_text = ""
    balance = float(etherscan.get_token_balance(hub_address, address, chain)) / 10 ** 18
    balance_dollar = float(price) * float(balance)
    balance_text = f"{balance:,.0f} {token.upper()} (${balance_dollar:,.0f})"

    return (
        f"{balance_text}\n\n"
        f"{threshold_text}\n\n"
        f"{split_text}\n\n"
        f"Liquidity Ratio Target: {liquidity_ratio_target}%\n"
        f"Earmarked Token Liquidity {token_liquidity_balance:,.0f} {token.upper()}"
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