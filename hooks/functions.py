import  os
from hooks import api, db
from constants import abis, ca, chains, tax

etherscan = api.Etherscan()


async def burn_x7r(amount, chain):
    try:
        chain_info, _ = chains.get_info(chain)

        sender_address = os.getenv("BURN_WALLET")
        recipient_address = ca.DEAD
        token_contract_address = ca.X7R(chain)
        sender_private_key = os.getenv("BURN_WALLET_PRIVATE_KEY")
        decimals = 18
        amount_to_send_wei = amount * (10 ** decimals)

        token_transfer_data = (
            '0xa9059cbb'
            + recipient_address[2:].rjust(64, '0')
            + hex(amount_to_send_wei)[2:].rjust(64, '0')
        )

        nonce = chain_info.w3.eth.get_transaction_count(sender_address)
        gas = chain_info.w3.eth.estimate_gas({
            'from': sender_address,
            'to': token_contract_address,
            'data': token_transfer_data,
        })
        gas_price = chain_info.w3.to_wei(chain_info.w3.eth.gas_price / 1e9, 'gwei')

        transaction = {
            'from': sender_address,
            'to': token_contract_address,
            'data': token_transfer_data,
            'gasPrice': gas_price,
            'gas': gas,
            'nonce': nonce,
            'chainId': int(chain_info.id)
        }

        signed_transaction = chain_info.w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = chain_info.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        return f"{amount} X7R Burnt\n\n{chain_info.scan_tx}{tx_hash.hex()}"
    except Exception as e:
        return f'Error burning X7R: {e}'


def estimate_gas(chain, function, loan_id = None):
    def calculate_cost(gas_estimate):
        eth_cost = gas_price * gas_estimate
        dollar_cost = (eth_cost / 10**9) * eth_price
        return f"{eth_cost / 10**9:.4f} {chain_info.native.upper()} (${dollar_cost:.2f})"

    chain_info, error_message = chains.get_info(chain)
    if not chain_info:
        return "Invalid chain or chain information unavailable."

    gas_price = chain_info.w3.eth.gas_price / 10**9
    eth_price = etherscan.get_native_price(chain)

    try:
        if function == "swap":
            return calculate_cost(tax.SWAP_GAS)
        
        elif function == "pair":
            data = "0xc9c65396" + ca.WETH(chain)[2:].rjust(64, '0') + ca.DEAD[2:].rjust(64, '0')
            gas_estimate = chain_info.w3.eth.estimate_gas({
                'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
                'to': chain_info.w3.to_checksum_address(ca.FACTORY(chain)),
                'data': data,
            })
            return calculate_cost(gas_estimate)

        elif function == "push":
            gas_estimate = chain_info.w3.eth.estimate_gas({
                'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
                'to': chain_info.w3.to_checksum_address(ca.TREASURY_SPLITTER(chain)),
                'data': "0x11ec9d34",
            })
            return calculate_cost(gas_estimate)

        elif function == "processfees":
            data = "0x61582eaa" + ca.X7R(chain)[2:].rjust(64, '0')
            gas_estimate = chain_info.w3.eth.estimate_gas({
                'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
                'to': chain_info.w3.to_checksum_address(ca.X7R_LIQ_HUB(chain)),
                'data': data, 
            })
            return calculate_cost(gas_estimate)

        elif function == "mint":
            gas_estimate = chain_info.w3.eth.estimate_gas({
                'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
                'to': chain_info.w3.to_checksum_address(ca.LPOOL_RESERVE(chain)),
                'data': "0xf6326fb3",
            })
            return calculate_cost(gas_estimate)

        elif function == "liquidate":
            chain_lpool = ca.LPOOL(chain)
            data = '0x415f1240' + hex(loan_id)[2:].rjust(64, '0')
            gas_estimate = chain_info.w3.eth.estimate_gas({
                'from': chain_info.w3.to_checksum_address(ca.DEPLOYER),
                'to': chain_info.w3.to_checksum_address(chain_lpool),
                'data': data,
            })
            return calculate_cost(gas_estimate)

        else:
            return "Unsupported function."
    except Exception:
        return "N/A"


def liquidate_loan(loan_id, chain, user_id):
    try:
        chain_info, _ = chains.get_info(chain)
        if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
            sender_address = os.getenv("BURN_WALLET")
            sender_private_key = os.getenv("BURN_WALLET_PRIVATE_KEY")
        else:
            wallet = db.wallet_get(user_id)
            sender_address = wallet["wallet"]
            sender_private_key = wallet["private_key"]

        chain_lpool = ca.LPOOL(chain)
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(chain_lpool), abi=abis.read("lendingpool")
        )

        liquidate_function_selector = '0x415f1240'
        loan_id_hex = hex(loan_id)[2:].rjust(64, '0')
        transaction_data = liquidate_function_selector + loan_id_hex

        nonce = chain_info.w3.eth.get_transaction_count(sender_address)
        gas_estimate = contract.functions.liquidate(loan_id).estimate_gas({"from": sender_address})
        gas_price = chain_info.w3.eth.gas_price

        transaction = {
            'from': sender_address,
            'to': chain_info.w3.to_checksum_address(chain_lpool),
            'data': transaction_data,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': int(chain_info.id)
        }

        signed_transaction = chain_info.w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = chain_info.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

        return f"Loan {loan_id} ({chain_info.name}) liquidated successfully.\n\n{chain_info.scan_tx}{tx_hash.hex()}"

    except Exception as e:
        return f"Error liquidating loan {loan_id} ({chain_info.name}): {str(e)}"


def splitter_push(contract_type, splitter_address, chain, user_id, token_address=None):
    try:
        chain_info, _ = chains.get_info(chain)

        if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
            sender_address = os.getenv("BURN_WALLET")
            sender_private_key = os.getenv("BURN_WALLET_PRIVATE_KEY")
        else:
            wallet = db.wallet_get(user_id)
            sender_address = wallet["wallet"]
            sender_private_key = wallet["private_key"]

        if contract_type == "splitter":
            function_selector = "0x11ec9d34"
            function_string = "pushing splitter"
            function_name = "pushAll"
            function_args = []
            
        if contract_type == "hub":
            function_selector = "0x61582eaa"
            function_string = "processing fees"
            function_name = "processFees"
            function_args = [token_address]

        transaction_data = function_selector
        nonce = chain_info.w3.eth.get_transaction_count(sender_address)

        contract = chain_info.w3.eth.contract(address=splitter_address, abi=etherscan.get_abi(splitter_address, chain))
        function_to_call = getattr(contract.functions, function_name)
        gas_estimate = function_to_call(*function_args).estimate_gas({"from": sender_address})
        gas_price = chain_info.w3.eth.gas_price

        transaction = {
            'from': sender_address,
            'to': splitter_address,
            'data': transaction_data,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': int(chain_info.id)
        }

        signed_transaction = chain_info.w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = chain_info.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

        return f"{chain_info.name} {function_string} Successful! TX: {chain_info.scan_tx}{tx_hash.hex()}"

    except Exception as e:
        return f"Error {function_string} ({chain_info.name}): {str(e)}"
    

def x7d_deposit(amount, chain, user_id):
    try:
        chain_info, _ = chains.get_info(chain)
        if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
            sender_address = os.getenv("BURN_WALLET")
            sender_private_key = os.getenv("BURN_WALLET_PRIVATE_KEY")
        else:
            wallet = db.wallet_get(user_id)
            sender_address = wallet["wallet"]
            sender_private_key = wallet["private_key"]

        address = ca.LPOOL_RESERVE(chain)
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(address), abi=etherscan.get_abi(address, chain)
        )

        nonce = chain_info.w3.eth.get_transaction_count(sender_address)

        gas_estimate = contract.functions.depositETH().estimate_gas({
            "from": sender_address,
            "value": chain_info.w3.to_wei(amount, 'ether')
        })
        gas_price = chain_info.w3.eth.gas_price

        transaction = {
            "from": sender_address,
            "to": chain_info.w3.to_checksum_address(address),
            "value": chain_info.w3.to_wei(amount, 'ether'),
            "gas": gas_estimate,
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": int(chain_info.id),
            "data": contract.encodeABI(fn_name="depositETH")
        }

        signed_transaction = chain_info.w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = chain_info.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

        return f"{amount} ETH ({chain_info.name}) deposited.\n\n{chain_info.scan_tx}{tx_hash.hex()}"

    except Exception as e:
        return f"Error depositing ETH ({chain_info.name}): {str(e)}"
 

def x7d_withdraw(amount, chain, user_id):
    try:
        chain_info, _ = chains.get_info(chain)

        if user_id == int(os.getenv("TELEGRAM_ADMIN_ID")):
            sender_address = os.getenv("BURN_WALLET")
            sender_private_key = os.getenv("BURN_WALLET_PRIVATE_KEY")
        else:
            wallet = db.wallet_get(user_id)
            sender_address = wallet["wallet"]
            sender_private_key = wallet["private_key"]

        address = ca.LPOOL_RESERVE(chain)
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(address),
            abi=etherscan.get_abi(address, chain)
        )

        amount_in_wei = chain_info.w3.to_wei(amount, 'ether')

        gas_estimate = contract.functions.withdrawETH(amount_in_wei).estimate_gas({"from": sender_address})
        gas_price = chain_info.w3.eth.gas_price

        function_selector = "0xf14210a6"
        encoded_amount = f"{amount_in_wei:064x}"
        data = function_selector + encoded_amount

        nonce = chain_info.w3.eth.get_transaction_count(sender_address)

        transaction = {
            'from': sender_address,
            'to': chain_info.w3.to_checksum_address(address),
            'data': data,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': int(chain_info.id)
        }

        signed_transaction = chain_info.w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = chain_info.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

        return f"Withdrew {amount} ETH ({chain_info.name}).\n\n{chain_info.scan_tx}{tx_hash.hex()}"

    except Exception as e:
        return f"Error withdrawing ETH ({chain_info.name}): {str(e)}"
