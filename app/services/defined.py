import os
import requests
from datetime import datetime, timedelta

from constants.protocol import chains


class Defined:
    def __init__(self):
        self.url = "https://graph.defined.fi/graphql"
        self.headers = {
            "content_type": "application/json",
            "Authorization": os.getenv("DEFINED_API_KEY"),
        }

    def get_price_change(self, address, chain):
        chain_info = chains.active_chains()[chain]

        current_timestamp = int(datetime.now().timestamp()) - 300
        one_hour_ago_timestamp = int(
            (datetime.now() - timedelta(hours=1)).timestamp()
        )
        twenty_four_hours_ago_timestamp = int(
            (datetime.now() - timedelta(hours=24)).timestamp()
        )
        seven_days_ago_timestamp = int(
            (datetime.now() - timedelta(days=7)).timestamp()
        )

        pricechange = f"""query {{
            getTokenPrices(
                inputs: [
                    {{ 
                        address: "{address}"
                        networkId: {chain_info.id}
                        timestamp: {current_timestamp}
                    }}
                    {{ 
                        address: "{address}"
                        networkId: {chain_info.id}
                        timestamp: {one_hour_ago_timestamp}
                    }}
                    {{ 
                        address: "{address}"
                        networkId: {chain_info.id}
                        timestamp: {twenty_four_hours_ago_timestamp}
                    }}
                    {{ 
                        address: "{address}"
                        networkId: {chain_info.id}
                        timestamp: {seven_days_ago_timestamp}
                    }}
                ]
            ) {{
                priceUsd
            }}
        }}"""
        try:
            response = requests.post(
                self.url, headers=self.headers, json={"query": pricechange}
            )
            data = response.json()

            current_price = data["data"]["getTokenPrices"][0]["priceUsd"]
            one_hour_ago_price = data["data"]["getTokenPrices"][1]["priceUsd"]
            twenty_four_hours_ago_price = data["data"]["getTokenPrices"][2][
                "priceUsd"
            ]
            seven_days_ago_price = data["data"]["getTokenPrices"][3][
                "priceUsd"
            ]

            one_hour_change = round(
                ((current_price - one_hour_ago_price) / one_hour_ago_price)
                * 100,
                2,
            )
            twenty_four_hours_change = round(
                (
                    (current_price - twenty_four_hours_ago_price)
                    / twenty_four_hours_ago_price
                )
                * 100,
                2,
            )
            seven_days_change = round(
                ((current_price - seven_days_ago_price) / seven_days_ago_price)
                * 100,
                2,
            )

            emoji_up = "📈"
            emoji_down = "📉"

            one_hour_change_str = f"{emoji_up if one_hour_change > 0 else emoji_down} 1H Change: {one_hour_change}%"
            twenty_four_hours_change_str = f"{emoji_up if twenty_four_hours_change > 0 else emoji_down} 24H Change: {twenty_four_hours_change}%"
            seven_days_change_str = f"{emoji_up if seven_days_change > 0 else emoji_down} 7D Change: {seven_days_change}%"

            result = (
                f"{one_hour_change_str}\n"
                f"{twenty_four_hours_change_str}\n"
                f"{seven_days_change_str}"
            )
        except Exception:
            result = "  1H Change: N/A\n  24H Change: N/A\n  7D Change: N/A"
        return result

    def get_token_image(self, token, chain):
        chain_info = chains.active_chains()[chain]

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

    def get_pair(self, address, chain):
        chain_info = chains.active_chains()[chain]

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

    def get_volume(self, pair, chain):
        try:
            chain_info = chains.active_chains()[chain]

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
            chain_info = chains.active_chains()[chain]
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
