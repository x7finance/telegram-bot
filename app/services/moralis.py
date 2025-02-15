import os
import requests

from constants.protocol import chains


class Moralis:
    def __init__(self):
        self.url = "https://deep-index.moralis.io/api/v2.2"
        self.api_key = os.getenv("MORALIS_API_KEY")
        self.headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

    def ping(self):
        try:
            url = f"{self.url}/latestBlockNumber/eth"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return True
            return f"🔴 Moralis: Connection failed: {response.status_code}"
        except requests.RequestException as e:
            return f"🔴 Morals: Connection failed: {str(e)}"

    def get_nft_stats(self, contract_address, chain):
        chain_info = chains.get_active_chains().get(chain)
        url = f"{self.url}/nft/{contract_address}/stats"
        params = {"chain": chain_info.name}

        response = requests.get(url, headers=self.headers, params=params)
        return (
            response.json()
            if response.status_code == 200
            else {"error": response.text}
        )
