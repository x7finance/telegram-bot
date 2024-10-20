# SPLITTERS

from web3 import Web3
from constants import ca, chains
from hooks import api

chainscan = api.ChainScan()


def generate_eco_split(chain, eth_value):
    if chain in chains.CHAINS:
        chain_info, _ = chains.get_info(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(ca.ECO_SPLITTER(chain)),
        abi=chainscan.get_abi(ca.ECO_SPLITTER(chain), chain),
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
        abi=chainscan.get_abi(ca.TREASURY_SPLITTER(chain), chain),
    )
    if chain == "eth" or chain  == "base":
        profit_percentage = contract.functions.outletShare(1).call() / 1000
        reward_pool_percentage = contract.functions.outletShare(2).call() / 1000
        community_multisig_percentage = contract.functions.outletShare(3).call() / 1000
        developers_multisig_percentage = contract.functions.outletShare(4).call() / 1000

    else:
        profit_percentage = 49
        reward_pool_percentage = contract.functions.outletShare(8).call() / 1000
        community_multisig_percentage = contract.functions.outletShare(9).call() / 1000
        developers_multisig_percentage = contract.functions.outletShare(10).call() / 1000
        
    profit_share = eth_value * profit_percentage / 100
    reward_pool_share = eth_value * reward_pool_percentage / 100
    developers_multisig_share = eth_value * developers_multisig_percentage / 100
    community_multisig_share = eth_value * community_multisig_percentage / 100
    
    return {
            "> DAO Multi Sig": (profit_share, profit_percentage), 
            "> Rewards Pool": (reward_pool_share, reward_pool_percentage),
            "> Community Multi Sig": (community_multisig_share, community_multisig_percentage),
            "> Operations Multi Sig": (developers_multisig_share, developers_multisig_percentage)
    }