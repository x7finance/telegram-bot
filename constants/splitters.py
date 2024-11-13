# SPLITTERS

from web3 import Web3
from constants import ca, chains
from hooks import api

etherscan = api.Etherscan()


def generate_eco_split(chain, eth_value):
    if chain in chains.CHAINS:
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
    
    x7r_share = eth_value * x7r_percentage / 100
    x7dao_share = eth_value * x7dao_percentage / 100
    x7100_share = eth_value * x7100_percentage / 100
    lending_pool_share = eth_value * lending_pool_percentage / 100
    treasury_share = eth_value * treasury_percentage / 100

    return {
        "> X7R Liquidity Hub": (x7r_share, x7r_percentage),
        "> X7DAO Liquidity Hub": (x7dao_share, x7r_percentage),
        "> X7100 Liquidity Hub": (x7100_share, x7100_percentage),
        "> Lending Pool": (lending_pool_share, lending_pool_percentage),
        "> Treasury Splitter": (treasury_share, treasury_percentage)
    }
    

def generate_treasury_split(chain, eth_value):
    if chain in chains.CHAINS:
        chain_info, _ = chains.get_info(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(ca.TREASURY_SPLITTER(chain)),
        abi=etherscan.get_abi(ca.TREASURY_SPLITTER(chain), chain),
    )
    
    profit_percentage = contract.functions.outletShare(1).call() / 1000
    reward_pool_percentage = contract.functions.outletShare(2).call() / 1000
    slot_1_percentage = contract.functions.outletShare(3).call() / 1000
    slot_2_percentage = contract.functions.outletShare(4).call() / 1000

    profit_share = eth_value * profit_percentage / 100
    reward_pool_share = eth_value * reward_pool_percentage / 100
    slot_1_share = eth_value * slot_1_percentage / 100
    slot_2_share = eth_value * slot_2_percentage / 100

    slot_names = {
        "eth": ("Pioneer Pool", "Community Multi Sig", "Developer Multi Sig"),
        "base": (),
        "bsc": (),
        "arb": (),
        "op": (),
        "poly": (),
    }
    
    rewards_pool_name, slot_1_name, slot_2_name = slot_names.get(chain, ("Rewards Pool", "Slot 1", "Slot 2"))

    return {
            "> DAO Multi Sig": (profit_share, profit_percentage), 
            f"> {rewards_pool_name}": (reward_pool_share, reward_pool_percentage),
            f"> {slot_1_name}": (slot_1_share, slot_1_percentage),
            f"> {slot_2_name}": (slot_2_share, slot_2_percentage)
    }