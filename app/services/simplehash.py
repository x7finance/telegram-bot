import os
import requests

from constants.protocol import chains


class Simplehash:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("SIMPLEHASH_API_KEY"),
        }
        self.url = "https://api.simplehash.com/api/v0/nfts/"

    def ping(self):
        try:
            response = requests.get(
                "https://api.simplehash.com/api/v0/chains",
                headers=self.headers,
                timeout=5,
            )
            if response.status_code == 200:
                return True
            return f"🔴 Simplehash: Connection failed: {response.status_code} {response.text}"
        except requests.RequestException as e:
            return f"🔴 Simplehash: Connection Failed: {e}"

    def get_nft_data(self, nft, chain):
        if chain == "eth":
            chain_name = "ethereum"
        else:
            chain_name = chains.get_active_chains().get(chain).name.lower()

        endpoint = f"collections/{chain_name}/{nft}?limit=1"
        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data

    def get_nft_by_id_data(self, nft, id, chain):
        if chain == "eth":
            chain_name = "ethereum"
        else:
            chain_name = chains.get_active_chains().get(chain).name.lower()

        endpoint = f"{chain_name}/{nft}/{id}"
        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data
