import os
import requests

from constants.protocol import chains


class Defined:
    def __init__(self):
        self.url = "https://graph.defined.fi/graphql"
        self.headers = {
            "content_type": "application/json",
            "Authorization": os.getenv("DEFINED_API_KEY"),
        }

    def ping(self):
        try:
            query = """query { getTokenPrices(inputs: []) { priceUsd } }"""
            response = requests.post(
                self.url,
                headers=self.headers,
                json={"query": query},
                timeout=5,
            )
            if response.status_code == 200:
                return True
            return f"🔴 Defined: Connection failed: {response.status_code}"
        except requests.RequestException as e:
            return f"🔴 Defined: Connection failed: {str(e)}"

    def get_pair(self, address, chain):
        chain_info, _ = chains.get_info(chain)

        pair_query = f"""query {{
            listPairsWithMetadataForToken (tokenAddress: "{address}" networkId: {chain_info.id}) {{
                results {{
                    pair {{
                        address
                    }}
                }}
            }}
            }}"""

        response = requests.post(
            self.url, headers=self.headers, json={"query": pair_query}
        )
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            pair = (
                data.get("data", {})
                .get("listPairsWithMetadataForToken", {})
                .get("results", [])[0]
                .get("pair", {})
                .get("address")
            )
            return pair
        else:
            return None

    def get_token_image(self, token, chain):
        chain_info, _ = chains.get_info(chain)

        image = f"""
            query {{
                getTokenInfo(address:"{token}", networkId:{chain_info.id}) {{
                    imageLargeUrl
                }}
            }}
        """

        response = requests.post(
            self.url, headers=self.headers, json={"query": image}
        )
        data = response.json()
        if "data" in data and "getTokenInfo" in data["data"]:
            token_info = data["data"]["getTokenInfo"]

            if token_info and "imageLargeUrl" in token_info:
                image_url = token_info["imageLargeUrl"]
                return image_url
            else:
                return None
        else:
            return None

    def get_volume(self, pair, chain):
        try:
            chain_info, _ = chains.get_info(chain)

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

            response = requests.post(
                self.url, headers=self.headers, json={"query": volume}
            )
            data = response.json()

            current_value = data["data"]["getDetailedPairStats"]["stats_day1"][
                "statsUsd"
            ]["volume"]["currentValue"]
            return "${:,.0f}".format(float(current_value))
        except Exception:
            return None

    def search(self, address, chain=None):
        if chain is not None:
            chain_info, _ = chains.get_info(chain)
            search_query = f"""query {{
                filterTokens(phrase:"{address}", rankings: {{attribute:liquidity}} limit:1, filters: {{network:[{chain_info.id}]}}) {{
                    results{{
                    token {{
                        address
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
                    }}
                }}
                }}
            }}"""

        response = requests.post(
            self.url, headers=self.headers, json={"query": search_query}
        )
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            results = (
                data.get("data", {}).get("filterTokens", {}).get("results", [])
            )

            if results:
                token_info = results[0].get("token", {})
                return token_info.get("address")

            return None
