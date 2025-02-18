from constants.protocol import abis, addresses, chains, tokens
from services import get_dextools, get_etherscan

dextools = get_dextools()
etherscan = get_etherscan()


async def get_eco_split(chain):
    if chain in chains.get_active_chains():
        chain_info, _ = chains.get_info(chain)

    address = addresses.eco_splitter(chain)
    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address),
        abi=abis.read("ecosystemsplitter"),
    )

    x7r_percentage = await contract.functions.outletShare(1).call() / 10
    x7dao_percentage = await contract.functions.outletShare(2).call() / 10
    x7100_percentage = await contract.functions.outletShare(3).call() / 10
    lending_pool_percentage = (
        await contract.functions.outletShare(4).call() / 10
    )
    treasury_percentage = await contract.functions.outletShare(5).call() / 10

    x7r_balance = await contract.functions.outletBalance(1).call() / 10**18
    x7dao_balance = await contract.functions.outletBalance(2).call() / 10**18
    x7100_balance = await contract.functions.outletBalance(3).call() / 10**18
    lending_pool_balance = (
        await contract.functions.outletBalance(4).call() / 10**18
    )
    treasury_balance = (
        await contract.functions.outletBalance(5).call() / 10**18
    )

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


async def get_hub_split(chain, address, token):
    if chain in chains.get_active_chains():
        chain_info, _ = chains.get_info(chain)

    settings = await get_push_settings(chain)
    abi = settings[token]["abi"]

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
        distribute = await contract.functions.distributeShare().call() / 10
        liquidity = await contract.functions.liquidityShare().call() / 10
        treasury = await contract.functions.treasuryShare().call() / 10
        liquidity_ratio_target = (
            await contract.functions.liquidityRatioTarget().call() / 10
        )
        balance_threshold = (
            await contract.functions.balanceThreshold().call() / 10**18
        )
        liquidity_balance = (
            await contract.functions.liquidityBalance().call() / 10**18
        )
        distribute_balance = (
            await contract.functions.distributeBalance().call() / 10**18
        )
        treasury_balance = (
            await contract.functions.treasuryBalance().call() / 10**18
        )
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

    if token.lower() in tokens.get_tokens():
        token_info = tokens.get_tokens()[token.lower()].get(chain)
        price, _ = dextools.get_price(token_info.ca, chain)

    if token == "x7r":
        try:
            token_liquidity_balance = (
                await contract.functions.x7rLiquidityBalance().call() / 10**18
            )
        except Exception:
            pass

    elif token == "x7dao":
        try:
            token_liquidity_balance = (
                await contract.functions.x7daoLiquidityBalance().call()
                / 10**18
            )
            auxiliary = await contract.functions.auxiliaryShare().call() / 10
            auxiliary_balance = (
                await contract.functions.auxiliaryBalance().call() / 10**18
            )
            split.update(
                {
                    "> Auxiliary Share": f"{auxiliary:.0f}% - {auxiliary_balance:,.4f} {chain_info.native.upper()}",
                }
            )
        except Exception:
            pass

    elif token in addresses.X7100:
        try:
            token_liquidity_balance = (
                await contract.functions.liquidityTokenBalance(
                    token_info.ca
                ).call()
                / 10**18
            )
            lending_pool = (
                await contract.functions.lendingPoolShare().call() / 10
            )
            lending_pool_balance = (
                await contract.functions.lendingPoolBalance().call() / 10**18
            )
            liquidity_balance_threshold = (
                await contract.functions.liquidityBalanceThreshold().call()
                / 10**18
            )
            split.update(
                {
                    "> Lending Pool Share": f"{lending_pool:.0f}% - {lending_pool_balance:,.4f} {chain_info.native.upper()}",
                }
            )
            threshold_text += f"\nLiquidity Balance Threshold: {liquidity_balance_threshold} {chain_info.native.upper()}"
        except Exception:
            pass

    balance = etherscan.get_token_balance(
        address, token_info.ca, 18, chain
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


def get_treasury_split(chain):
    if chain in chains.get_active_chains():
        chain_info, _ = chains.get_info(chain)

    address = addresses.treasury_splitter(chain)
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


async def get_push_settings(chain):
    async def calculate_eco_tokens(contract):
        return await contract.functions.outletBalance(4).call() / 10**18

    async def calculate_treasury_tokens(_):
        return etherscan.get_native_balance(
            addresses.treasury_splitter(chain), chain
        )

    async def calculate_x7r_tokens(contract):
        balance = float(
            etherscan.get_token_balance(
                addresses.x7r_liquidity_hub(chain),
                addresses.x7r(chain),
                18,
                chain,
            )
        )
        contract_balance = (
            await contract.functions.x7rLiquidityBalance().call() / 10**18
        )
        return balance - contract_balance

    async def calculate_x7dao_tokens(contract):
        balance = float(
            etherscan.get_token_balance(
                addresses.x7dao_liquidity_hub(chain),
                addresses.x7dao(chain),
                18,
                chain,
            )
        )
        contract_balance = (
            await contract.functions.x7daoLiquidityBalance().call() / 10**18
        )
        return balance - contract_balance

    async def calculate_x7100_tokens(contract, token_address):
        balance = float(
            etherscan.get_token_balance(
                addresses.x7100_liquidity_hub(chain),
                token_address,
                18,
                chain,
            )
        )
        contract_balance = (
            await contract.functions.liquidityTokenBalance(
                token_address
            ).call()
            / 10**18
        )
        return balance - contract_balance

    return {
        "eco": {
            "address": addresses.eco_splitter(chain),
            "abi": abis.read("ecosystemsplitter"),
            "name": "Ecosystem Splitter",
            "threshold": 0.01 if chain.lower() == "eth" else 0.0001,
            "contract_type": "splitter",
            "calculate_tokens": calculate_eco_tokens,
            "recipient": addresses.lending_pool_reserve(chain),
        },
        "treasury": {
            "address": addresses.treasury_splitter(chain),
            "abi": abis.read("treasurysplitter"),
            "name": "Treasury Splitter",
            "threshold": 0.01 if chain.lower() == "eth" else 0.0001,
            "contract_type": "splitter",
            "calculate_tokens": calculate_treasury_tokens,
            "recipient": addresses.dao_multisig(chain),
        },
        "x7r": {
            "address": addresses.x7r_liquidity_hub(chain),
            "abi": abis.read("x7rliquidityhub"),
            "name": "X7R Liquidity Hub",
            "token_address": addresses.x7r(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": calculate_x7r_tokens,
        },
        "x7dao": {
            "address": addresses.x7dao_liquidity_hub(chain),
            "abi": abis.read("x7daoliquidityhub"),
            "name": "X7DAO Liquidity Hub",
            "token_address": addresses.x7dao(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": calculate_x7dao_tokens,
        },
        "x7101": {
            "address": addresses.x7100_liquidity_hub(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": addresses.x7101(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda contract: calculate_x7100_tokens(
                contract, addresses.x7101(chain)
            ),
        },
        "x7102": {
            "address": addresses.x7100_liquidity_hub(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": addresses.x7102(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda contract: calculate_x7100_tokens(
                contract, addresses.x7102(chain)
            ),
        },
        "x7103": {
            "address": addresses.x7100_liquidity_hub(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": addresses.x7103(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda contract: calculate_x7100_tokens(
                contract, addresses.x7103(chain)
            ),
        },
        "x7104": {
            "address": addresses.x7100_liquidity_hub(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": addresses.x7104(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda contract: calculate_x7100_tokens(
                contract, addresses.x7104(chain)
            ),
        },
        "x7105": {
            "address": addresses.x7100_liquidity_hub(chain),
            "abi": abis.read("x7100liquidityhub"),
            "name": "X7100 Liquidity Hub",
            "token_address": addresses.x7105(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "calculate_tokens": lambda contract: calculate_x7100_tokens(
                contract, addresses.x7105(chain)
            ),
        },
    }
