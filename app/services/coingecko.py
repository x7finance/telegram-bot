import requests

from utils import tools


class Coingecko:
    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/"

    def ping(self):
        try:
            response = requests.get(f"{self.url}ping", timeout=5)
            if response.status_code == 200:
                return True
            return f"🔴 CoinGecko: Connection failed: {response.status_code}"
        except requests.RequestException as e:
            return f"🔴 CoinGecko: Connection failed: {str(e)}"

    def get_ath(self, token):
        endpoint = (
            f"coins/{token.lower()}?localization=false&tickers=false&market_data="
            "true&community_data=false&developer_data=false&sparkline=false"
        )
        response = requests.get(self.url + endpoint)
        if response.status_code == 200:
            data = response.json()
            value = data["market_data"]
            return (
                value["ath"]["usd"],
                value["ath_change_percentage"]["usd"],
                value["ath_date"]["usd"],
            )
        else:
            return None

    def get_nft_floor(self, nft):
        endpoint = f"nfts/ethereum/contract/{nft}"
        response = requests.get(self.url + endpoint)
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            floor_price = data["floor_price"]["native_currency"]
            floor_price_usd = data["floor_price"]["usd"]

            return {
                "floor_price": floor_price,
                "floor_price_usd": floor_price_usd,
            }
        else:
            return None

    def get_price(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
        response = requests.get(self.url + endpoint)

        if response.status_code != 200:
            return None

        data = response.json()

        if token not in data:
            return None

        price = float(data[token]["usd"])
        if "e-" in str(price) or price < 1:
            price = "{:.8f}".format(price)
        else:
            price = "{:,.2f}".format(price)

        volume = tools.format_millions(
            float(data[token].get("usd_24h_vol", 0))
        )
        market_cap = tools.format_millions(
            float(data[token].get("usd_market_cap", 0))
        )

        price_change = round(data[token].get("usd_24h_change", 0), 2)

        return {
            "price": price,
            "change": price_change,
            "mcap": market_cap,
            "volume": volume,
        }

    def search(self, token):
        endpoint = f"search?query={token}"
        response = requests.get(self.url + endpoint)
        return response.json()

    def get_mcap(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_market_cap=true"
        response = requests.get(self.url + endpoint)
        data = response.json()
        return data[token]["usd_market_cap"]
