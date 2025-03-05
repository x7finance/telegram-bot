import aiohttp
from utils import tools


class Coingecko:
    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/"

    async def ping(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.url}ping", timeout=5
                ) as response:
                    if response.status == 200:
                        return True
                    return (
                        f"🔴 CoinGecko: Connection failed: {response.status}"
                    )
        except Exception as e:
            return f"🔴 CoinGecko: Connection failed: {str(e)}"

    async def get_ath(self, token):
        endpoint = (
            f"coins/{token.lower()}?localization=false&tickers=false&market_data="
            "true&community_data=false&developer_data=false&sparkline=false"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    value = data["market_data"]
                    return (
                        value["ath"]["usd"],
                        value["ath_change_percentage"]["usd"],
                        value["ath_date"]["usd"],
                    )
                return None

    async def get_price(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + endpoint) as response:
                if response.status != 200:
                    return None

                data = await response.json()

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

    async def search(self, token):
        endpoint = f"search?query={token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + endpoint) as response:
                return await response.json()

    async def get_mcap(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_market_cap=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + endpoint) as response:
                data = await response.json()
                return data[token]["usd_market_cap"]
