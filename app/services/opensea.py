import os
import requests


class Opensea:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_API_KEY"),
        }
        self.url = "https://api.opensea.io/v2/"

    def get_nft_collection(self, slug):
        endpoint = f"collections/{slug}"
        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data

    def get_nft_id(self, nft, identifier):
        endpoint = f"chain/ethereum/contract/{nft}/nfts/{identifier}"
        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data
