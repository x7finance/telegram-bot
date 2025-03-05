import os
import aiohttp
import time

from constants.protocol import addresses, chains


class Etherscan:
    def __init__(self):
        self.url = "https://api.etherscan.io/v2/api"
        self.key = os.getenv("ETHERSCAN_API_KEY")

    async def ping(self):
        try:
            params = {
                "module": "proxy",
                "action": "eth_blockNumber",
                "apikey": self.key,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url, params=params, timeout=5
                ) as response:
                    if response.status == 200:
                        return True
                    return (
                        f"🔴 Etherscan: Connection failed: {response.status}"
                    )
        except Exception as e:
            return f"🔴 Etherscan: Connection failed: {str(e)}"

    async def get_abi(self, contract, chain):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=contract&action=getsourcecode&address={contract}&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data["result"][0]["ABI"]

    async def get_block(self, chain, time):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=block&action=getblocknobytime&timestamp={time}&closest=before&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data["result"]

    async def get_daily_tx_count(self, contract, chain):
        chain_info, _ = await chains.get_info(chain)
        yesterday = int(time.time()) - 86400
        block_yesterday = await self.get_block(chain, yesterday)
        block_now = await self.get_block(chain, int(time.time()))

        tx_url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(tx_url) as response:
                tx_data = await response.json()
                tx_entry_count = (
                    len(tx_data["result"])
                    if tx_data and "result" in tx_data
                    else 0
                )

        internal_tx_url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlistinternal&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(internal_tx_url) as response:
                internal_tx_data = await response.json()
                internal_tx_entry_count = (
                    len(internal_tx_data["result"])
                    if internal_tx_data and "result" in internal_tx_data
                    else 0
                )

        return tx_entry_count + internal_tx_entry_count

    async def get_burnt_supply(self, token, chain):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={token}&address={addresses.DEAD}&tag=latest&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return int(data["result"][:-18])

    async def get_gas(self, chain):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=gastracker&action=gasoracle&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_native_balance(self, wallet, chain):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=balancemulti&address={wallet}&tag=latest&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return float(data["result"][0]["balance"]) / 10**18

    async def get_native_price(self, chain):
        chain_info, _ = await chains.get_info(chain)

        if chain == "poly":
            field = "maticusd"
            token = "matic"
        else:
            token = chain_info.native
            field = "ethusd"

        url = f"{self.url}?chainid={chain_info.id}&module=stats&action={token}price&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return float(data["result"][field]) / 1**18

    async def get_supply(self, token, chain):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=stats&action=tokensupply&contractaddress={token}&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data["result"]

    async def get_token_balance(self, wallet, token, decimals, chain):
        try:
            chain_info, _ = await chains.get_info(chain)
            url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest&apikey={self.key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return float(data["result"]) / 10**decimals
        except Exception:
            return 0

    async def get_tx(self, address, chain):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&sort=desc&address={address}&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_internal_tx(self, address, chain):
        chain_info, _ = await chains.get_info(chain)
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlistinternal&sort=desc&address={address}&apikey={self.key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
