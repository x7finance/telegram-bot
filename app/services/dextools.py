import os
import requests

from constants.protocol import chains


class Dextools:
    def __init__(self):
        self.plan = "trial"
        self.headers = {
            "accept": "application/json",
            "x-api-key": os.getenv("DEXTOOLS_API_KEY"),
        }
        self.url = f"http://public-api.dextools.io/{self.plan}/v2/"

    def get_audit(self, address, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"token/{chain_info.dext}/{address}/audit"
        response = requests.get(self.url + endpoint, headers=self.headers)
        return response.json()

    def get_dex(self, address, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"pool/{chain_info.dext}/{address}"

        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        try:
            if data is not None:
                if (
                    "data" in data
                    and "exchange" in data["data"]
                    and "name" in data["data"]["exchange"]
                ):
                    return f"({data['data']['exchange']['name']} pair)"
                else:
                    return ""
            else:
                return ""
        except Exception:
            return ""

    def get_price(self, address, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"token/{chain_info.dext}/{address}/price"

        response = requests.get(self.url + endpoint, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") is not None and "price" in data["data"]:
                price = data["data"]["price"]
                if "e-" in str(price):
                    price = "{:.8f}".format(price)
                elif price < 1:
                    price = "{:.8f}".format(price)
                else:
                    price = "{:.2f}".format(price)

                one_hour_change = data["data"]["variation1h"]
                six_hour_change = data["data"]["variation6h"]
                one_day_change = data["data"]["variation24h"]

                emoji_up = "📈"
                emoji_down = "📉"
                one_hour = (
                    f"{emoji_up if one_hour_change is not None and one_hour_change > 0 else emoji_down} 1H Change: {round(one_hour_change, 2)}%"
                    if one_hour_change is not None
                    else f"{emoji_down} 1H Change: 0%"
                )
                six_hour = (
                    f"{emoji_up if six_hour_change is not None and six_hour_change > 0 else emoji_down} 6H Change: {round(six_hour_change, 2)}%"
                    if six_hour_change is not None
                    else f"{emoji_down} 6H Change: 0%"
                )
                one_day = (
                    f"{emoji_up if one_day_change is not None and one_day_change > 0 else emoji_down} 24H Change: {round(one_day_change, 2)}%"
                    if one_day_change is not None
                    else f"{emoji_down} 24H Change: 0%"
                )

                change = f"{one_hour}\n{six_hour}\n{one_day}"

            else:
                price = None
                change = "📉 1HR Change: N/A\n📉 6HR Change: N/A\n📉 24HR Change: N/A"

            return price, change
        else:
            change = (
                "📉 1HR Change: N/A\n📉 6HR Change: N/A\n📉 24HR Change: N/A"
            )
            return None, change

    def get_token_info(self, address, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"token/{chain_info.dext}/{address}/info"
        response = requests.get(self.url + endpoint, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            if data and "data" in data and data["data"]:
                total_supply = data["data"].get("totalSupply", 0)
                mcap = data["data"].get("mcap", 0)
                holders = data["data"].get("holders", 0)

                if mcap is not None:
                    formatted_mcap = "${:,.0f}".format(mcap)
                else:
                    fdv = data["data"].get("fdv", 0)
                    if fdv is not None:
                        formatted_mcap = f"${fdv:,.0f}"
                    else:
                        formatted_mcap = None

                return {
                    "supply": total_supply,
                    "mcap": formatted_mcap,
                    "holders": holders,
                }
            else:
                return {"supply": None, "mcap": None, "holders": None}
        else:
            return {"supply": None, "mcap": None, "holders": None}

    def get_token_name(self, address, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"token/{chain_info.dext}/{address}"
        response = requests.get(self.url + endpoint, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data and "data" in data and data["data"]:
                name = data["data"].get("name", "Unknown Token")
                symbol = data["data"].get("symbol", "")

                return {"name": name, "symbol": symbol}
            else:
                return {"name": "Unknown Token", "symbol": ""}
        else:
            return {"name": "Unknown Token", "symbol": ""}

    def get_liquidity(self, address, chain):
        chain_info = chains.active_chains()[chain]

        endpoint = f"pool/{chain_info.dext}/{address}/liquidity"
        response = requests.get(self.url + endpoint, headers=self.headers)

        liquidity_data = {"total": "0", "token": "0", "eth": "0.00"}

        if response.status_code == 200:
            data = response.json()
            if data and "data" in data:
                total = data["data"].get("liquidity", 0)
                token = data["data"]["reserves"].get("mainToken", 0)
                eth = data["data"]["reserves"].get("sideToken", 0)

                liquidity_data = {
                    "total": f"${'{:,.0f}'.format(total)}" if total else None,
                    "token": f"{'{:,.0f}'.format(token)}" if token else None,
                    "eth": f"{'{:,.2f}'.format(eth)}" if eth else None,
                }

        return liquidity_data

    def get_pool_price(self, address, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"pool/{chain_info.dext}/{address}/price"
        price = 0

        response = requests.get(self.url + endpoint, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data and "data" in data:
                price = data["data"].get("price", 0)

        return price
