import os
import requests
import time

from constants.protocol import addresses, chains


class Etherscan:
    def __init__(self):
        self.url = "https://api.etherscan.io/v2/api"
        self.key = os.getenv("ETHERSCAN_API_KEY")

    def ping(self):
        try:
            params = {
                "module": "proxy",
                "action": "eth_blockNumber",
                "apikey": self.key,
            }
            response = requests.get(self.url, params=params, timeout=5)
            if response.status_code == 200:
                return True
            return f"🔴 Etherscan: Connection failed: {response.status_code}"
        except requests.RequestException as e:
            return f"🔴 Etherscan: Connection failed: {str(e)}"

    def get_abi(self, contract, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=contract&action=getsourcecode&address={contract}&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return data["result"][0]["ABI"]

    def get_block(self, chain, time):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=block&action=getblocknobytime&timestamp={time}&closest=before&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return data["result"]

    def get_daily_tx_count(self, contract, chain):
        chain_info = chains.get_active_chains()[chain]
        yesterday = int(time.time()) - 86400
        block_yesterday = self.get_block(chain, yesterday)
        block_now = self.get_block(chain, int(time.time()))
        tx_url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        tx_response = requests.get(tx_url)
        tx_data = tx_response.json()
        if tx_data:
            tx_entry_count = (
                len(tx_data["result"]) if "result" in tx_data else 0
            )
        else:
            tx_data = 0
        internal_tx_url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        internal_tx_response = requests.get(internal_tx_url)
        internal_tx_data = internal_tx_response.json()
        if internal_tx_data:
            internal_tx_entry_count = (
                len(internal_tx_data["result"])
                if "result" in internal_tx_data
                else 0
            )
        else:
            internal_tx_data = 0
        entry_count = tx_entry_count + internal_tx_entry_count
        return entry_count

    def get_gas(self, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=gastracker&action=gasoracle&apikey={self.key}"
        response = requests.get(url)
        return response.json()

    def get_native_balance(self, wallet, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=balancemulti&address={wallet}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return float(data["result"][0]["balance"]) / 10**18

    def get_native_price(self, chain):
        chain_info = chains.get_active_chains()[chain]

        if chain == "poly":
            field = "maticusd"
            token = "matic"
        else:
            token = chain_info.native
            field = "ethusd"

        url = f"{self.url}?chainid={chain_info.id}&module=stats&action={token}price&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return float(data["result"][field]) / 1**18

    def get_stables_balance(self, wallet, token, chain):
        try:
            chain_info = chains.get_active_chains()[chain]
            url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest&apikey={self.key}"
            response = requests.get(url)
            data = response.json()
            return int(data["result"][:-6])
        except Exception:
            return 0

    def get_supply(self, token, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=stats&action=tokensupply&contractaddress={token}&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return data["result"]

    def get_token_balance(self, wallet, token, decimals, chain):
        try:
            chain_info = chains.get_active_chains()[chain]
            url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest&apikey={self.key}"
            response = requests.get(url)
            data = response.json()
            return float(data["result"]) / 10**decimals
        except Exception:
            return 0

    def get_tx_from_hash(self, tx, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=proxy&action=eth_getTransactionByHash&txhash={tx}&apikey={self.key}"
        response = requests.get(url)
        return response.json()

    def get_tx(self, address, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&sort=desc&address={address}&apikey={self.key}"
        response = requests.get(url)
        return response.json()

    def get_internal_tx(self, address, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlistinternal&sort=desc&address={address}&apikey={self.key}"
        response = requests.get(url)
        return response.json()

    def get_verified(self, contract, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=contract&action=getsourcecode&address={contract}&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return True if "SourceCode" in data["result"][0] else False

    def get_x7r_supply(self, chain):
        chain_info = chains.get_active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={addresses.x7r(chain)}&address={addresses.DEAD}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        supply = addresses.SUPPLY - int(data["result"][:-18])
        return supply
