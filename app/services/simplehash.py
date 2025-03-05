import aiohttp
import os
from constants.protocol import chains


class Simplehash:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("SIMPLEHASH_API_KEY"),
        }
        self.url = "https://api.simplehash.com/api/v0/nfts/"

    async def ping(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.simplehash.com/api/v0/chains",
                    headers=self.headers,
                    timeout=5,
                ) as response:
                    if response.status == 200:
                        return True
                    return f"🔴 Simplehash: Connection failed: {response.status} {await response.text()}"
        except Exception as e:
            return f"🔴 Simplehash: Connection Failed: {e}"

    async def get_nft_data(self, nft, chain):
        if chain == "eth":
            chain_name = "ethereum"
        else:
            chain_info, _ = await chains.get_info(chain)
            chain_name = chain_info.name.lower()

        endpoint = f"collections/{chain_name}/{nft}?limit=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url + endpoint, headers=self.headers
            ) as response:
                data = await response.json()
                return data

    async def get_nft_by_id_data(self, nft, id, chain):
        if chain == "eth":
            chain_name = "ethereum"
        else:
            chain_info, _ = await chains.get_info(chain)
            chain_name = chain_info.name.lower()

        endpoint = f"{chain_name}/{nft}/{id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url + endpoint, headers=self.headers
            ) as response:
                data = await response.json()
                return data
