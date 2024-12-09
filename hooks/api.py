import requests, os, time, tweepy

from farcaster import Warpcast
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI

from constants import ca, chains
        

class Blockspan:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.url = "https://api.blockspan.com/v1/"
        self.headers = {
                    "accept": "application/json",
                    "X-API-KEY": os.getenv("BLOCKSPAN_API_KEY"),
                }


    def get_nft_data(self, nft, chain):
        try:
            chain_info = chains.active_chains()[chain]
            endpoint = f"collections/contract/{nft}?chain={chain_info.blockspan}"
            response = requests.get(
                self.url + endpoint,
                headers=self.headers
            )
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


class Etherscan:
    def __init__(self):
        self.url = "https://api.etherscan.io/v2/api"
        self.key = os.getenv('ETHERSCAN_API_KEY')
        

    def get_abi(self, contract: str, chain: str) -> str:
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=contract&action=getsourcecode&address={contract}&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return data["result"][0]["ABI"]


    def get_block(self, chain: str, time: "int") -> str:
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=block&action=getblocknobytime&timestamp={time}&closest=before&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return data["result"]


    def get_daily_tx_count(self, contract: str, chain: str, ) -> int:
        chain_info = chains.active_chains()[chain]
        yesterday = int(time.time()) - 86400
        block_yesterday = self.get_block(chain, yesterday)
        block_now = self.get_block(chain, int(time.time()))
        tx_url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        tx_response = requests.get(tx_url)
        tx_data = tx_response.json()
        if tx_data:
            tx_entry_count = len(tx_data['result']) if 'result' in tx_data else 0
        else:
            tx_data = 0
        internal_tx_url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        internal_tx_response = requests.get(internal_tx_url)
        internal_tx_data = internal_tx_response.json()
        if internal_tx_data:
            internal_tx_entry_count = len(internal_tx_data['result']) if 'result' in internal_tx_data else 0
        else:
            internal_tx_data = 0
        entry_count = tx_entry_count + internal_tx_entry_count
        return entry_count


    def get_gas(self, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=gastracker&action=gasoracle&apikey={self.key}"
        response = requests.get(url)
        return response.json()


    def get_native_balance(self, wallet, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=balancemulti&address={wallet}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return float(data["result"][0]["balance"]) / 10 ** 18


    def get_native_price(self, chain):
        chain_info = chains.active_chains()[chain]

        if chain == "poly":
            field = "maticusd"
            token = "matic"
        else:
            token = chain_info.native
            field = "ethusd"
        
        url = f"{self.url}?chainid={chain_info.id}&module=stats&action={token}price&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return float(data["result"][field]) / 1**18


    def get_stables_balance(self, wallet, token, chain):
        try:
            chain_info = chains.active_chains()[chain]
            url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest&apikey={self.key}"
            response = requests.get(url)
            data = response.json()
            return int(data["result"][:-6])
        except Exception as e:
            return 0


    def get_supply(self, token, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=stats&action=tokensupply&contractaddress={token}&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return data["result"]


    def get_token_balance(self, wallet, token, chain):
        try:
            chain_info = chains.active_chains()[chain]
            url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest&apikey={self.key}"
            response = requests.get(url)
            data = response.json()
            return int(data["result"][:-18])
        except Exception:
            return 0


    def get_tx_from_hash(self, tx, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=proxy&action=eth_getTransactionByHash&txhash={tx}&apikey={self.key}"
        response = requests.get(url)
        return response.json()


    def get_tx(self, address, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlist&sort=desc&address={address}&apikey={self.key}"
        response = requests.get(url)
        return response.json()


    def get_internal_tx(self, address, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=txlistinternal&sort=desc&address={address}&apikey={self.key}"
        response = requests.get(url)
        return response.json()


    def get_verified(self, contract, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=contract&action=getsourcecode&address={contract}&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return True if "SourceCode" in data["result"][0] else False


    def get_x7r_supply(self, chain):
        chain_info = chains.active_chains()[chain]
        url = f"{self.url}?chainid={chain_info.id}&module=account&action=tokenbalance&contractaddress={ca.X7R(chain)}&address={ca.DEAD}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        supply = ca.SUPPLY - int(data["result"][:-18])
        return supply


class Dextools:
    def __init__(self):
        self.plan = "trial"
        self.headers = {
        'accept': 'application/json',
        'x-api-key': os.getenv("DEXTOOLS_API_KEY")}
        self.url = f"http://public-api.dextools.io/{self.plan}/v2/"


    def get_dex(self, pair, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f'pool/{chain_info.dext}/{pair}'

        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        try:
            if data is not None:
                if "data" in data and "exchange" in data["data"] and "name" in data["data"]["exchange"]:
                    return f'({data["data"]["exchange"]["name"]} pair)'
                else:
                    return ""
            else:
                return ""
        except Exception:
            ""
    

    def get_price(self, token, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f'token/{chain_info.dext}/{token.lower()}/price'

        response = requests.get(self.url + endpoint, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('data') is not None and 'price' in data['data']:
                price = data['data']['price']
                if "e-" in str(price):
                    price = "{:.8f}".format(price)
                elif price < 1:
                    price = "{:.8f}".format(price) 
                else:
                    price = "{:.2f}".format(price)

                one_hour_change = data['data']['variation1h']
                six_hour_change = data['data']['variation6h']
                one_day_change = data['data']['variation24h']

                emoji_up = "📈"
                emoji_down = "📉"
                one_hour = f"{emoji_up if one_hour_change is not None and one_hour_change > 0 else emoji_down} 1H Change: {round(one_hour_change, 2)}%" if one_hour_change is not None else f'{emoji_down} 1H Change: 0%'
                six_hour = f"{emoji_up if six_hour_change is not None and six_hour_change > 0 else emoji_down} 6H Change: {round(six_hour_change, 2)}%" if six_hour_change is not None else f'{emoji_down} 6H Change: 0%'
                one_day = f"{emoji_up if one_day_change is not None and one_day_change > 0 else emoji_down} 24H Change: {round(one_day_change, 2)}%" if one_day_change is not None else f'{emoji_down} 24H Change: 0%'

                change = f"{one_hour}\n{six_hour}\n{one_day}"

            else:
                price = None
                change = f"📉 1HR Change: N/A\n📉 6HR Change: N/A\n📉 24HR Change: N/A"

            return price, change
        else:
            change = f"📉 1HR Change: N/A\n📉 6HR Change: N/A\n📉 24HR Change: N/A"
            return None, change
        

    def get_token_info(self, pair, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"token/{chain_info.dext}/{pair}/info"
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
                        formatted_mcap = f'${fdv:,.0f} (FDV)'
                    else:
                        formatted_mcap = None

                return {
                    "supply": total_supply,
                    "mcap": formatted_mcap,
                    "holders": holders
                }
            else:
                return {
                    "total_supply": None,
                    "mcap": None,
                    "holders": None
                }
        else:
            return {
                "supply": None,
                "mcap": None,
                "holders": None
            }
       
        
    def get_token_name(self, address, chain):
        chain_info = chains.active_chains()[chain]
        endpoint = f"token/{chain_info.dext}/{address.lower()}"
        response = requests.get(self.url + endpoint, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data and "data" in data and data["data"]:
                name = data["data"].get("name", "Unknown Token")
                symbol = data["data"].get("symbol", "")

                return {
                    "name": name,
                    "symbol": symbol
                }
            else:
                return {
                    "name": "Unknown Token",
                    "symbol": ""
                }
        else:
            return {
                "name": "Unknown Token",
                "symbol": ""
            }


    def get_liquidity(self, pair, chain):
        chain_info = chains.active_chains()[chain]

        endpoint = f'pool/{chain_info.dext}/{pair}/liquidity'
        response = requests.get(self.url + endpoint, headers=self.headers)

        liquidity_data = {
            "total": "0",
            "token": "0",
            "eth": "0.00"
        }

        if response.status_code == 200:
            data = response.json()
            if data and "data" in data:
                total = data['data'].get('liquidity', 0)
                token = data['data']['reserves'].get('mainToken', 0)
                eth = data['data']['reserves'].get('sideToken', 0)

                liquidity_data = {
                    "total": f"${'{:,.0f}'.format(total)}" if total else None,
                    "token": f"{'{:,.0f}'.format(token)}" if token else None,
                    "eth": f"{'{:,.2f}'.format(eth)}" if eth else None
                }

        return liquidity_data
    
    
    def get_pool_price(self, chain, pair):
        chain_info = chains.active_chains()[chain]
        endpoint = f'pool/{chain_info.dext}/{pair}/price'
        price = 0
        
        response = requests.get(self.url + endpoint, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data and "data" in data:
                price = data['data'].get('price', 0)

        return price


class CoinGecko:
    def __init__(self):
        self.url = f"https://api.coingecko.com/api/v3/"


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
        endpoint = (
            f"nfts/ethereum/contract/{nft}"
        )
        response = requests.get(self.url + endpoint)
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            floor_price = data["floor_price"]["native_currency"]
            floor_price_usd = data["floor_price"]["usd"]

            return {"floor_price": floor_price, "floor_price_usd": floor_price_usd}
        else:
            return None

    
    def get_price(self, token):
        coingecko = CoinGeckoAPI()
        data = coingecko.get_price(
            ids=token,
            vs_currencies="usd",
            include_24hr_change="true",
            include_24hr_vol="true",
            include_market_cap="true")
        if "e-" in str(data[token]["usd"]):
            price = "{:.8f}".format(data[token]["usd"])
        elif data[token]["usd"] < 1:
            price = "{:.8f}".format(data[token]["usd"]) 
        else:
            price = "{:,.0f}".format(data[token]["usd"])

        if "e-" in str(data[token]["usd_24h_vol"]):
            volume = "${:.8f}".format(data[token]["usd_24h_vol"])
        elif data[token]["usd_24h_vol"] < 1:
            volume = "${:.8f}".format(data[token]["usd_24h_vol"]) 
        else:
            volume = "${:,.0f}".format(data[token]["usd_24h_vol"])
            
        price_change = data[token]["usd_24h_change"]
        if price_change is None:
            price_change = 0
        else:
            price_change = round(data[token]["usd_24h_change"], 2)
        market_cap = data[token]["usd_market_cap"]
        if market_cap is None or market_cap == 0:
            market_cap_formatted = None
        else:
            market_cap_formatted = "${:0,.0f}".format(float(market_cap))

        return {"price": price, "change": price_change, "mcap": market_cap_formatted, "volume": volume}


    def search(self, token):
        endpoint = f"search?query={token}"
        response = requests.get(self.url + endpoint)
        return response.json()


    def get_mcap(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_market_cap=true"
        response = requests.get(self.url + endpoint)
        data = response.json()
        return data[token]["usd_market_cap"]


class Defined:
    def __init__(self):
        self.url = "https://graph.defined.fi/graphql"
        self.headers = {
            "content_type": "application/json",
            "Authorization": os.getenv("DEFINED_API_KEY")
        }


    def get_price_change(self, address, chain):
        chain_info = chains.active_chains()[chain]

        current_timestamp = int(datetime.now().timestamp()) - 300
        one_hour_ago_timestamp = int((datetime.now() - timedelta(hours=1)).timestamp())
        twenty_four_hours_ago_timestamp = int((datetime.now() - timedelta(hours=24)).timestamp())
        seven_days_ago_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

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
            response = requests.post(self.url, headers=self.headers, json={"query": pricechange})
            data = response.json()

            current_price = data["data"]["getTokenPrices"][0]["priceUsd"]
            one_hour_ago_price = data["data"]["getTokenPrices"][1]["priceUsd"]
            twenty_four_hours_ago_price = data["data"]["getTokenPrices"][2]["priceUsd"]
            seven_days_ago_price = data["data"]["getTokenPrices"][3]["priceUsd"]

            one_hour_change = round(((current_price - one_hour_ago_price) / one_hour_ago_price) * 100, 2)
            twenty_four_hours_change = round(
                ((current_price - twenty_four_hours_ago_price) / twenty_four_hours_ago_price) * 100, 2)
            seven_days_change = round(((current_price - seven_days_ago_price) / seven_days_ago_price) * 100, 2)

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
        except Exception as e:
            result = "  1H Change: N/A\n  24H Change: N/A\n  7D Change: N/A"
        return result


    def get_token_image(self, token, chain):
        chain_info = chains.active_chains()[chain]

        image = f'''
            query {{
                getTokenInfo(address:"{token}", networkId:{chain_info.id}) {{
                    imageLargeUrl
                }}
            }}
        '''

        response = requests.post(self.url, headers=self.headers, json={"query": image})
        data = response.json()
        if 'data' in data and 'getTokenInfo' in data['data']:
                token_info = data['data']['getTokenInfo']

                if token_info and 'imageLargeUrl' in token_info:
                    image_url = token_info['imageLargeUrl']
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
        
        response = requests.post(self.url, headers=self.headers, json={"query": pair_query})
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            pair = data.get('data', {}).get('listPairsWithMetadataForToken', {}).get('results', [])[0].get('pair', {}).get('address')
            return pair
        else:
            return None


    def get_volume(self, pair, chain):
        try:
            chain_info = chains.active_chains()[chain]

            volume = f'''
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
                '''

            response = requests.post(self.url, headers=self.headers, json={"query": volume})
            data = response.json()

            current_value = data['data']['getDetailedPairStats']['stats_day1']['statsUsd']['volume']['currentValue']
            return "${:,.0f}".format(float(current_value))
        except Exception as e:
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
        
        response = requests.post(self.url, headers=self.headers, json={"query": search_query})
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            token_info = data.get('data', {}).get('filterTokens', {}).get('results', [{}])[0].get('token', {})
            if token_info:
                return token_info.get('address')
            return None
        else:
            return None


class WarpcastApi:
    def __init__(self):
        self.client = Warpcast(mnemonic=os.getenv("WARPCAST_API_KEY"))
        self.fid = "419688"
        self.username = "x7finance"


    def get_cast(self, name=None):
        try:
            if name is None:
                data = self.client.get_casts(self.fid, None, 1)
            else:
                username = self.client.get_user_by_username(name)
                data = self.client.get_casts(username.fid, None, 1)
            return data.casts
        except Exception:
            return None


    def get_followers(self):
        data = self.client.get_me()
        return data.follower_count
    

    def get_recasters(self, hash):
        data = self.client.get_cast_recasters(hash)
        return data.users


class GitHub:
    def __init__(self):
        self.url = "https://api.github.com/repos/x7finance/monorepo/"
        self.headers = {
        "Authorization": f"token {os.getenv('GITHUB_PAT')}"
    }


    def get_issues(self):
        endpoint = "issues"
        issues = []
        page = 1

        while True:
            response = requests.get(self.url + endpoint, headers=self.headers, params={"state": "open", "page": page, "per_page": 100})
            if response.status_code != 200:
                break

            data = response.json()
            if not data:
                break
            
            issues.extend([issue for issue in data if "pull_request" not in issue])
            page += 1

        if not issues:
            return "No open issues found."

        formatted_issues = []
        for issue in issues:
            title = issue.get("title", "No Title")
            creator = issue.get("user", {}).get("login", "Unknown")
            created_at = issue.get("created_at", "Unknown")
            labels = ", ".join([label.get("name", "") for label in issue.get("labels", [])])
            url = issue.get("html_url", "No URL")
            
            if created_at != "Unknown":
                created_at = datetime.fromisoformat(created_at.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
            
            formatted_issues.append(
                f"{title} ({labels})\n"
                f"Creator: {creator}\n"
                f"Created At: {created_at}\n"
                f"URL: {url}\n"
            )
        
        issue_count = len(issues)
        return f"Total Open Issues: {issue_count}\n\n" + "\n".join(formatted_issues)
    

    def get_latest_commit(self):
        endpoint = "commits"

        response = requests.get(self.url + endpoint, headers=self.headers)
        if response.status_code != 200:
            return f"Error fetching commits: {response.status_code}, {response.text}"

        commits = response.json()
        if not commits:
            return "No commits found."

        latest_commit = commits[0]
        message = latest_commit.get("commit", {}).get("message", "No message")
        created_by = latest_commit.get("commit", {}).get("author", {}).get("name", "Unknown author")
        created_at = latest_commit.get("commit", {}).get("author", {}).get("date", "Unknown date")
        url = latest_commit.get("html_url", "No URL")

        if created_at != "Unknown":
            created_at = datetime.fromisoformat(created_at.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
            
        return f"Latest Commit:\n{message}\nCreated By: {created_by}\nCreated At: {created_at}\nURL: {url}"


    def get_pull_requests(self):
        endpoint = "pulls"
        pull_requests = []
        page = 1

        while True:
            response = requests.get(self.url + endpoint, headers=self.headers, params={"state": "open", "page": page, "per_page": 100})
            if response.status_code != 200:
                break

            data = response.json()
            if not data:
                break
            
            pull_requests.extend(data)
            page += 1

        if not pull_requests:
            return "No open pull requests found."

        formatted_prs = []
        for pr in pull_requests:
            title = pr.get("title", "No Title")
            creator = pr.get("user", {}).get("login", "Unknown")
            date = pr.get("created_at", "Unknown")
            url = pr.get("html_url", "No URL")
            
            if date != "Unknown":
                date = datetime.fromisoformat(date.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
            
            formatted_prs.append(
                f"{title}\n"
                f"Creator: {creator}\n"
                f"Created At: {date}\n"
                f"URL: {url}\n"
            )
        
        count = len(pull_requests)
        return f"Total Open Pull Requests: {count}\n\n" + "\n".join(formatted_prs)


class Opensea:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("OPENSEA_API_KEY")
        }
        self.url = f"https://api.opensea.io/v2/"
        

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


class Snapshot:
    def __init__(self):
        self.url = "https://hub.snapshot.org/graphql"


    def get_latest(self):
        query = {
            "query": 'query { proposals ( first: 1, skip: 0, where: { space_in: ["x7finance.eth"]}, '
                    'orderBy: "created", orderDirection: desc ) { id title start end snapshot state choices '
                    "scores scores_total author }}"
        }
        response = requests.get(self.url, query)
        return response.json()


class Twitter:
    def __init__(self):
        auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"))
        auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))
        self.api = tweepy.API(auth)


    def fetch_latest_tweet(self, username):
        try:
            tweets = self.api.user_timeline(screen_name=username, count=1, tweet_mode="extended")
            if tweets:
                tweet = tweets[0]
                tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
                return {
                    "text": tweet.full_text,
                    "url": tweet_url,
                    "likes": tweet.favorite_count,
                    "retweets": tweet.retweet_count,
                    "replies": tweet.reply_count if hasattr(tweet, "reply_count") else "0",
                    "created_at": tweet.created_at,
                }
            else:
                return {"error": "No tweets found for this user."}
        except Exception:
            return None