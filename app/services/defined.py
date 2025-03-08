import aiohttp
import certifi
import os
import ssl

from constants.protocol import chains


class Defined:
    def __init__(self):
        self.url = "https://graph.defined.fi/graphql"
        self.headers = {
            "content_type": "application/json",
            "Authorization": os.getenv("DEFINED_API_KEY"),
        }
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def ping(self):
        try:
            query = """query { getTokenPrices(inputs: []) { priceUsd } }"""
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    headers=self.headers,
                    json={"query": query},
                    timeout=5,
                    ssl=self.ssl_context,
                ) as response:
                    if response.status == 200:
                        return True
                    return f"🔴 Defined: Connection failed: {response.status}"
        except Exception as e:
            return f"🔴 Defined: Connection failed: {str(e)}"

    async def get_pair(self, address, chain):
        chain_info, _ = await chains.get_info(chain)

        pair_query = f"""query {{
            listPairsWithMetadataForToken (tokenAddress: "{address}" networkId: {chain_info.id}) {{
                results {{
                    pair {{
                        address
                    }}
                }}
            }}
            }}"""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers=self.headers,
                json={"query": pair_query},
                ssl=self.ssl_context,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    results = (
                        data.get("data", {})
                        .get("listPairsWithMetadataForToken", {})
                        .get("results", [])
                    )

                    if results:
                        return results[0].get("pair", {}).get("address")
                return None

    async def get_token_image(self, token, chain):
        chain_info, _ = await chains.get_info(chain)

        image = f"""
            query {{
                getTokenInfo(address:"{token}", networkId:{chain_info.id}) {{
                    imageLargeUrl
                }}
            }}
        """

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers=self.headers,
                json={"query": image},
                ssl=self.ssl_context,
            ) as response:
                data = await response.json()
                if "data" in data and "getTokenInfo" in data["data"]:
                    token_info = data["data"]["getTokenInfo"]

                    if token_info and "imageLargeUrl" in token_info:
                        image_url = token_info["imageLargeUrl"]
                        return image_url
                return None

    async def get_volume(self, pair, chain):
        try:
            chain_info, _ = await chains.get_info(chain)

            volume = f"""
                query {{
                getDetailedPairStats(pairAddress: "{pair}", networkId: {chain_info.id}, bucketCount: 1, tokenOfInterest: token1) {{
                    stats_day1 {{
                    statsUsd {{
                        volume {{
                        currentValue
                        }}
                    }}
                    }}
                }}
                }}
                """

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    headers=self.headers,
                    json={"query": volume},
                    ssl=self.ssl_context,
                ) as response:
                    data = await response.json()

                    current_value = data["data"]["getDetailedPairStats"][
                        "stats_day1"
                    ]["statsUsd"]["volume"]["currentValue"]
                    return "${:,.0f}".format(float(current_value))
        except Exception:
            return None

    async def search(self, address, chain=None):
        if chain is not None:
            chain_info, _ = await chains.get_info(chain)
            search_query = f"""query {{
                filterTokens(phrase:"{address}", rankings: {{attribute:liquidity}} limit:1, filters: {{network:[{chain_info.id}]}}) {{
                    results{{
                    token {{
                        address
                        name
                        symbol
                    }}
                }}
                }}
            }}"""
        else:
            search_query = f"""query {{
                filterTokens(phrase:"{address}", rankings: {{attribute:liquidity}} limit:1) {{
                    results{{
                    token {{
                        address
                        name
                        symbol
                    }}
                }}
                }}
            }}"""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers=self.headers,
                json={"query": search_query},
                ssl=self.ssl_context,
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    results = (
                        data.get("data", {})
                        .get("filterTokens", {})
                        .get("results", [])
                    )

                    if results:
                        token_info = results[0].get("token", {})
                        return token_info.get("address")

                return None
