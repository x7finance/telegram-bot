import os
import requests
from datetime import datetime

from constants.protocol import addresses, chains


class Blockspan:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.url = "https://api.blockspan.com/v1/"
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("BLOCKSPAN_API_KEY"),
        }

    def ping(self):
        try:
            endpoint = (
                f"collections/contract/{addresses.PIONEER}?chain=eth-main"
            )
            response = requests.get(self.url + endpoint, headers=self.headers)
            if response.status_code == 200:
                return True
            return f"🔴 Blockspan: Connection failed: {response.status_code} - {response.text}"
        except requests.RequestException as e:
            return f"🔴 Blockspan: Connection failed: {str(e)}"

    def get_nft_data(self, nft, chain):
        try:
            chain_info = chains.get_active_chains()[chain]
            endpoint = (
                f"collections/contract/{nft}?chain={chain_info.blockspan}"
            )
            response = requests.get(self.url + endpoint, headers=self.headers)
            data = response.json()

            info = {"total_tokens": 0, "floor_price": 0}

            total_tokens = data.get("total_tokens", None)
            if total_tokens is not None:
                info["total_tokens"] = int(total_tokens)

            exchange_data = data.get("exchange_data")
            if exchange_data is not None:
                for item in exchange_data:
                    stats = item.get("stats")
                    if stats is not None:
                        floor_price = stats.get("floor_price")
                        if floor_price is not None:
                            info["floor_price"] = floor_price
                            break
            return info

        except Exception:
            return {"total_tokens": None, "floor_price": None}
