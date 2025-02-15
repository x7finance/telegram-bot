import os
import requests


class Opensea:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_API_KEY"),
        }
        self.url = "https://api.opensea.io/api/v2/"

    def ping(self):
        try:
            response = requests.get(
                self.url + "collections/opensea",
                headers=self.headers,
                timeout=5,
            )
            if response.status_code == 200:
                return True
            return f"🔴 OpenSea: Connection failed: {response.status_code} {response.text}"
        except requests.RequestException as e:
            return f"🔴 OpenSea: Connection Failed: {e}"

    def get_nft_by_id(self, nft, identifier):
        endpoint = f"chain/ethereum/contract/{nft}/nfts/{identifier}"
        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data

    def get_nft_by_slug(self, slug):
        endpoint = f"collections/{slug}/stats"
        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data
