import  os
from hooks import api
from constants import abis, ca, chains

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
    

def liquidate_loan(loan_id, chain):
    try:
        chain_info, _ = chains.get_info(chain)
        sender_address = os.getenv("BURN_WALLET")
        sender_private_key = os.getenv("BURN_WALLET_PRIVATE_KEY")
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

        return f"Loan {loan_id} liquidated successfully.\n\n{chain_info.scan_tx}{tx_hash.hex()}"

    except Exception as e:
        return f"Error liquidating Loan ID {loan_id}: {e}"


def splitter_push(contract_type, splitter_address, chain, token_address=None):
    try:
        chain_info, _ = chains.get_info(chain)
        sender_address = os.getenv("BURN_WALLET")
        sender_private_key = os.getenv("BURN_WALLET_PRIVATE_KEY")

        if contract_type == "splitter":
            function_selector = "0x11ec9d34"
            function_string = "Splitter push"
            function_name = "pushAll"
            function_args = []
            
        if contract_type == "hub":
            function_selector = "0x61582eaa"
            function_string = "Fees process"
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
        return f"{chain_info.name} {function_string} Error: {e}"
