from decimal import Decimal

from constants.protocol import abis, addresses, chains, tax, tokens
from services import get_etherscan, get_dbmanager

etherscan = get_etherscan()
db = get_dbmanager()


async def estimate_gas(chain, function, loan_id=None):
    def calculate_cost(gas_estimate):
        eth_cost = gas_price * gas_estimate
        dollar_cost = (eth_cost / 10**9) * eth_price
        return f"{eth_cost / 10**9:.6f} {chain_info.native.upper()} (${dollar_cost:.2f})"

    chain_info, _ = chains.get_info(chain)

    gas_price = await chain_info.w3.eth.gas_price / 10**9
    eth_price = etherscan.get_native_price(chain)

    try:
        if function == "swap":
            return calculate_cost(tax.SWAP_GAS)

        elif function == "pair":
            data = (
                "0xc9c65396"
                + addresses.weth(chain)[2:].rjust(64, "0")
                + addresses.DEAD[2:].rjust(64, "0")
            )
            gas_estimate = await chain_info.w3.eth.estimate_gas(
                {
                    "from": chain_info.w3.to_checksum_address(
                        addresses.DEPLOYER
                    ),
                    "to": chain_info.w3.to_checksum_address(
                        addresses.factory(chain)
                    ),
                    "data": data,
                }
            )
            return calculate_cost(gas_estimate)

        elif function == "push":
            gas_estimate = await chain_info.w3.eth.estimate_gas(
                {
                    "from": chain_info.w3.to_checksum_address(
                        addresses.DEPLOYER
                    ),
                    "to": chain_info.w3.to_checksum_address(
                        addresses.treasury_splitter(chain)
                    ),
                    "data": "0x11ec9d34",
                }
            )
            return calculate_cost(gas_estimate)

        elif function == "processfees":
            data = "0x61582eaa" + addresses.x7r(chain)[2:].rjust(64, "0")
            gas_estimate = await chain_info.w3.eth.estimate_gas(
                {
                    "from": chain_info.w3.to_checksum_address(
                        addresses.DEPLOYER
                    ),
                    "to": chain_info.w3.to_checksum_address(
                        addresses.x7r_liquidity_hub(chain)
                    ),
                    "data": data,
                }
            )
            return calculate_cost(gas_estimate)

        elif function == "mint":
            gas_estimate = await chain_info.w3.eth.estimate_gas(
                {
                    "from": chain_info.w3.to_checksum_address(
                        addresses.DEPLOYER
                    ),
                    "to": chain_info.w3.to_checksum_address(
                        addresses.lending_pool_reserve(chain)
                    ),
                    "data": "0xf6326fb3",
                }
            )
            return calculate_cost(gas_estimate)

        elif function == "liquidate":
            data = "0x415f1240" + hex(loan_id)[2:].rjust(64, "0")
            gas_estimate = await chain_info.w3.eth.estimate_gas(
                {
                    "from": chain_info.w3.to_checksum_address(
                        addresses.DEPLOYER
                    ),
                    "to": chain_info.w3.to_checksum_address(
                        addresses.lending_pool(chain)
                    ),
                    "data": data,
                }
            )
            return calculate_cost(gas_estimate)

        else:
            return "Unsupported function."
    except Exception:
        return "N/A"


async def liquidate_loan(loan_id, chain, user_id):
    try:
        chain_info, _ = chains.get_info(chain)

        wallet = db.wallet_get(user_id)
        sender_address = wallet["wallet"]
        sender_private_key = wallet["private_key"]

        address = addresses.lending_pool(chain)
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(address),
            abi=abis.read("lendingpool"),
        )

        nonce = await chain_info.w3.eth.get_transaction_count(sender_address)

        gas_price = await chain_info.w3.eth.gas_price
        gas_estimate = contract.functions.liquidate(loan_id).estimate_gas(
            {"from": sender_address}
        )

        transaction = contract.functions.liquidate(loan_id).build_transaction(
            {
                "from": sender_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce,
                "chainId": int(chain_info.id),
            }
        )

        signed_tx = chain_info.w3.eth.account.sign_transaction(
            transaction, sender_private_key
        )
        tx_hash = await chain_info.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = await chain_info.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=30
        )

        if receipt.status == 1:
            return f"Loan {loan_id} ({chain_info.name.upper()}) liquidated successfully\n\n{chain_info.scan_tx}0x{tx_hash.hex()}"
        else:
            return f"Error: Transaction failed while liquidating loan {loan_id} ({chain_info.name.upper()})"

    except Exception as e:
        return f"Error: {str(e)}"


async def splitter_push(
    contract_type, address, abi, chain, user_id, token_address=None
):
    try:
        chain_info, _ = chains.get_info(chain)

        wallet = db.wallet_get(user_id)
        sender_address = wallet["wallet"]
        sender_private_key = wallet["private_key"]

        if contract_type == "splitter":
            function_name = "pushAll"
            function_args = []
        elif contract_type == "hub":
            function_name = "processFees"
            function_args = [token_address]

        contract = chain_info.w3.eth.contract(address=address, abi=abi)

        function_to_call = getattr(contract.functions, function_name)
        nonce = await chain_info.w3.eth.get_transaction_count(sender_address)
        gas_price = await chain_info.w3.eth.gas_price
        gas_estimate = function_to_call(*function_args).estimate_gas(
            {"from": sender_address}
        )

        transaction = function_to_call(*function_args).build_transaction(
            {
                "from": sender_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce,
                "chainId": int(chain_info.id),
            }
        )

        signed_tx = chain_info.w3.eth.account.sign_transaction(
            transaction, sender_private_key
        )
        tx_hash = await chain_info.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = await chain_info.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=30
        )
        if receipt.status == 1:
            return f"{function_name} ({chain_info.name.upper()}) called successfully\n\n{chain_info.scan_tx}0x{tx_hash.hex()}"
        else:
            return f"Error: Transaction failed on {function_name} ({chain_info.name.upper()})"

    except Exception as e:
        return f"Error: {str(e)}"


async def stuck_tx(chain, user_id, gas_multiplier=1.5):
    try:
        chain_info, _ = chains.get_info(chain)

        wallet = db.wallet_get(user_id)
        sender_address = wallet["wallet"]
        sender_private_key = wallet["private_key"]

        latest_nonce = await chain_info.w3.eth.get_transaction_count(
            sender_address, "latest"
        )
        pending_nonce = await chain_info.w3.eth.get_transaction_count(
            sender_address, "pending"
        )

        if pending_nonce == latest_nonce:
            return "No pending transactions found. No action needed."

        gas_price = await chain_info.w3.eth.gas_price
        adjusted_gas_price = int(gas_price * gas_multiplier)

        transaction = {
            "from": sender_address,
            "to": sender_address,
            "value": 0,
            "gas": 21000,
            "gasPrice": adjusted_gas_price,
            "nonce": pending_nonce,
            "chainId": int(chain_info.id),
        }

        signed_tx = chain_info.w3.eth.account.sign_transaction(
            transaction, sender_private_key
        )
        tx_hash = await chain_info.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = await chain_info.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=30
        )
        if receipt.status == 1:
            return f"Stuck transaction (Nonce: {pending_nonce}) successfully replaced ({chain_info.name.upper()})\n\n{chain_info.scan_tx}0x{tx_hash.hex()}"
        else:
            return f"Error: Transaction (Nonce: {pending_nonce}) failed to be replaced ({chain_info.name.upper()})"

    except Exception as e:
        return f"Error: {str(e)}"


async def withdraw_native(amount, chain, user_id, recipient_address):
    try:
        chain_info, _ = chains.get_info(chain)

        wallet = db.wallet_get(user_id)
        sender_address = wallet["wallet"]
        sender_private_key = wallet["private_key"]

        amount_in_wei = chain_info.w3.to_wei(amount, "ether")
        nonce = await chain_info.w3.eth.get_transaction_count(sender_address)

        gas_price = await chain_info.wc.eth.gas_price
        gas_estimate = await chain_info.w3.eth.estimate_gas(
            {
                "from": sender_address,
                "to": recipient_address,
                "value": amount_in_wei,
            }
        )

        transaction = {
            "from": sender_address,
            "to": recipient_address,
            "value": amount_in_wei,
            "gas": gas_estimate,
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": int(chain_info.id),
        }

        signed_tx = chain_info.w3.eth.account.sign_transaction(
            transaction, sender_private_key
        )
        tx_hash = await chain_info.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = await chain_info.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=30
        )
        if receipt.status == 1:
            return f"Successfully withdrew {amount} {chain_info.native.upper()} ({chain_info.name.upper()})\n\n{chain_info.scan_tx}0x{tx_hash.hex()}"
        else:
            return f"Error: Transaction failed during withdrawal ({chain_info.name.upper()})"

    except Exception as e:
        return f"Error: {str(e)}"


async def withdraw_tokens(
    user_id, amount, token_address, decimals, recipient, chain
):
    try:
        chain_info, _ = chains.get_info(chain)

        wallet = db.wallet_get(user_id)
        sender_address = wallet["wallet"]
        sender_private_key = wallet["private_key"]
        amount = Decimal(str(amount))
        amount_to_send_wei = int(amount * (10**decimals))

        token_name = "Tokens"

        for (
            token_name_candidate,
            token_info_dict,
        ) in tokens.get_tokens().items():
            for chain_name, token_info in token_info_dict.items():
                if token_address.lower() == token_info.ca.lower():
                    token_name = token_name_candidate.upper()
                    break
            if token_name != "Tokens":
                break

        if recipient == addresses.DEAD:
            action, actioned = "burning", "burnt"
        else:
            action, actioned = "transferring", "transfered"

        token_transfer_data = (
            "0xa9059cbb"
            + recipient[2:].rjust(64, "0")
            + hex(amount_to_send_wei)[2:].rjust(64, "0")
        )

        nonce = await chain_info.w3.eth.get_transaction_count(sender_address)

        gas_price = await chain_info.w3.eth.gas_price
        gas_estimate = await chain_info.w3.eth.estimate_gas(
            {
                "from": sender_address,
                "to": token_address,
                "data": token_transfer_data,
            }
        )

        transaction = {
            "from": sender_address,
            "to": token_address,
            "data": token_transfer_data,
            "gasPrice": gas_price,
            "gas": gas_estimate,
            "nonce": nonce,
            "chainId": int(chain_info.id),
        }

        signed_tx = chain_info.w3.eth.account.sign_transaction(
            transaction, sender_private_key
        )
        tx_hash = await chain_info.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )
        receipt = await chain_info.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=30
        )

        if receipt.status == 1:
            return f"{amount} {token_name} ({chain_info.name.upper()}) {actioned}\n\n{chain_info.scan_tx}0x{tx_hash.hex()}"
        else:
            return f"Error: Transaction failed while {action} {amount} {token_name} ({chain_info.name.upper()})"

    except Exception as e:
        return f"Error: {e}"


async def x7d_mint(amount, chain, user_id):
    try:
        chain_info, _ = chains.get_info(chain)

        wallet = db.wallet_get(user_id)
        sender_address = wallet["wallet"]
        sender_private_key = wallet["private_key"]

        address = addresses.lending_pool_reserve(chain)
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(address),
            abi=abis.read("lendingpoolreserve"),
        )

        nonce = await chain_info.w3.eth.get_transaction_count(sender_address)

        gas_price = await chain_info.w3.eth.gas_price
        gas_estimate = contract.functions.depositETH().estimate_gas(
            {
                "from": sender_address,
                "value": chain_info.w3.to_wei(amount, "ether"),
            }
        )

        transaction = contract.functions.depositETH().build_transaction(
            {
                "from": sender_address,
                "value": chain_info.w3.to_wei(amount, "ether"),
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce,
                "chainId": int(chain_info.id),
            }
        )

        signed_tx = chain_info.w3.eth.account.sign_transaction(
            transaction, sender_private_key
        )
        tx_hash = await chain_info.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = await chain_info.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=30
        )
        if receipt.status == 1:
            return f"{amount} X7D ({chain_info.name.upper()}) minted successfully\n\n{chain_info.scan_tx}0x{tx_hash.hex()}"
        else:
            return f"Error: Transaction failed while minting X7D ({chain_info.name.upper()})"

    except Exception as e:
        return f"Error: {str(e)}"


async def x7d_redeem(amount, chain, user_id):
    try:
        chain_info, _ = chains.get_info(chain)

        wallet = db.wallet_get(user_id)
        sender_address = wallet["wallet"]
        sender_private_key = wallet["private_key"]

        address = addresses.lending_pool_reserve(chain)
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(address),
            abi=abis.read("lendingpoolreserve"),
        )

        nonce = await chain_info.w3.eth.get_transaction_count(sender_address)

        gas_price = await chain_info.w3.eth.gas_price
        gas_estimate = contract.functions.withdrawETH(
            chain_info.w3.to_wei(amount, "ether")
        ).estimate_gas({"from": sender_address})

        transaction = contract.functions.withdrawETH(
            chain_info.w3.to_wei(amount, "ether")
        ).build_transaction(
            {
                "from": sender_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce,
                "chainId": int(chain_info.id),
            }
        )

        signed_tx = chain_info.w3.eth.account.sign_transaction(
            transaction, sender_private_key
        )
        tx_hash = await chain_info.w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = await chain_info.w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=30
        )
        if receipt.status == 1:
            return f"Redeemed {amount} X7D ({chain_info.name.upper()}) successfully\n\n{chain_info.scan_tx}0x{tx_hash.hex()}"
        else:
            return f"Error: Transaction failed while redeeming X7D ({chain_info.name.upper()})"

    except Exception as e:
        return f"Error: {str(e)}"
