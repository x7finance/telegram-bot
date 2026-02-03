import aiohttp
import asyncio
import os
from datetime import datetime
from constants.protocol import chains
from utils import cache


class Dune(cache.CachedService):
    def __init__(self):
        self.api_key = os.getenv("DUNE_API_KEY")
        self.header = {"x-dune-api-key": self.api_key}
        self.base_url = "https://api.dune.com/api/v1/"
        self.time_allowed = 6 * 60 * 60

        self.top_pairs_id = "2970801"
        self.volume_id = "2972368"

        self.volume_text = ""
        self.volume_flag = False
        self.volume_timestamp = datetime.now().timestamp()
        self.volume_last_date = datetime.fromtimestamp(
            self.volume_timestamp
        ).strftime("%Y-%m-%d %H:%M:%S")

        self.top_text = {}
        self.top_flag = {}
        self.top_timestamp = {}
        self.top_last_date = {}
        self.error = "Unable to get Dune data. Please use the link below"

        super().__init__()

    async def ping(self, cache_ttl=None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}query/{self.volume_id}/execute",
                    headers=self.header,
                    params={"performance": "small"},
                    timeout=5,
                ) as response:
                    if response.status == 200:
                        return True
                    return f"🔴 Dune: Connection failed: {response.status}"
        except Exception as e:
            return f"🔴 Dune: Connection failed: {str(e)}"

    def make_api_url(self, module, action, identifier):
        return f"{self.base_url}{module}/{identifier}/{action}"

    async def execute_query(self, query_id, engine="small", cache_ttl=600):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.make_api_url("query", "execute", query_id),
                headers=self.header,
                params={"performance": engine},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("execution_id")
                else:
                    response.raise_for_status()

    async def get_query_status(self, execution_id, cache_ttl=600):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.make_api_url("execution", "status", execution_id),
                headers=self.header,
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    async def get_query_results(self, execution_id, cache_ttl=600):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.make_api_url("execution", "results", execution_id),
                headers=self.header,
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    async def cancel_query_execution(self, execution_id, cache_ttl=600):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.make_api_url("execution", "cancel", execution_id),
                headers=self.header,
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    async def get_top_tokens(self, chain, cache_ttl=600):
        chain_info, error_message = (
            await chains.get_info(chain) if chain else (None, None)
        )
        if error_message:
            return error_message
        chain_name = (
            "ethereum"
            if chain == "eth"
            else (chain_info.name.lower() if chain_info else "all")
        )
        chain_name_title = (
            f"({chain_info.name})" if chain_info else "(All chains)"
        )

        if chain_name.upper() not in self.top_flag:
            self.top_text[chain_name.upper()] = ""
            self.top_flag[chain_name.upper()] = False
            self.top_timestamp[chain_name.upper()] = datetime.now().timestamp()
            self.top_last_date[chain_name.upper()] = datetime.fromtimestamp(
                self.top_timestamp[chain_name.upper()]
            ).strftime("%Y-%m-%d %H:%M:%S")

        if (
            datetime.now().timestamp() - self.top_timestamp[chain_name.upper()]
            < self.time_allowed
            and self.top_text[chain_name.upper()]
        ):
            next_update_time = (
                self.top_timestamp[chain_name.upper()] + self.time_allowed
            )
            remaining_time = max(
                0, int(next_update_time - datetime.now().timestamp())
            )
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_remaining_text = (
                f"Next update available in: {hours}h {minutes}m {seconds}s"
            )

            return (
                f"{self.top_text[chain_name.upper()]}"
                f"Last Updated: {self.top_last_date[chain_name.upper()]}\n"
                f"{time_remaining_text}"
            )

        execution_id = await self.execute_query(self.top_pairs_id, "medium")
        response_data = None
        for attempt in range(4):
            try:
                response_data = await self.get_query_results(execution_id)
            except ValueError:
                return (
                    f"*Xchange Top Pairs {chain_name_title}*\n\n{self.error}"
                )

            if response_data.get("is_execution_finished", False):
                break
            await asyncio.sleep(5)

        if not response_data or "result" not in response_data:
            return f"*Xchange Top Pairs {chain_name_title}*\n\n{self.error}"

        rows = response_data["result"]["rows"]
        if chain:
            rows = [
                row
                for row in rows
                if row.get("pair")
                and row["pair"].lower() != "total"
                and row.get("blockchain", "").strip().lower()
                == chain_name.strip().lower()
            ]
        else:
            rows = [
                row
                for row in rows
                if row.get("pair") and row["pair"].lower() != "total"
            ]

        valid_rows = [
            row
            for row in rows
            if row.get("last_24hr_amt") is not None
            and isinstance(row["last_24hr_amt"], (int, float))
        ]

        sorted_rows = sorted(
            valid_rows, key=lambda x: x.get("last_24hr_amt", 0), reverse=True
        )
        top_pairs = sorted_rows[:3] if len(sorted_rows) >= 3 else sorted_rows

        top_text = f"*Xchange Top Pairs {chain_name_title}*\n\n"

        if not any(item.get("pair") for item in top_pairs):
            return f"*Xchange Top Pairs {chain_name_title}*\n\n{self.error}"

        for idx, item in enumerate(top_pairs, start=1):
            pair = item.get("pair")
            last_24hr_amt = item.get("last_24hr_amt")
            blockchain = item.get("blockchain")
            if pair and last_24hr_amt:
                top_text += f"{idx}. {pair} ({blockchain.upper()})\n24 Hour Volume: ${last_24hr_amt:,.0f}\n\n"

        self.top_flag[chain_name.upper()] = True
        self.top_text[chain_name.upper()] = top_text
        self.top_timestamp[chain_name.upper()] = datetime.now().timestamp()
        self.top_last_date[chain_name.upper()] = datetime.fromtimestamp(
            self.top_timestamp[chain_name.upper()]
        ).strftime("%Y-%m-%d %H:%M:%S")

        return top_text

    async def get_volume(self, cache_ttl=600):
        if (
            datetime.now().timestamp() - self.volume_timestamp
            < self.time_allowed
            and self.volume_text
        ):
            next_update_time = self.volume_timestamp + self.time_allowed
            remaining_time = max(
                0, int(next_update_time - datetime.now().timestamp())
            )
            hours, remainder = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            next_update_text = (
                f"Next update available in: {hours}h {minutes}m {seconds}s"
            )

            return (
                f"*Xchange Trading Volume*\n\n"
                f"{self.volume_text}\n\n"
                f"Last Updated: {self.volume_last_date} UTC\n"
                f"{next_update_text}"
            )

        execution_id = await self.execute_query(self.volume_id, "medium")
        response_data = None
        max_retries = 30

        for attempt in range(max_retries):
            response = await self.get_query_results(execution_id)
            if not isinstance(response, dict):
                return f"*Xchange Volume*\n\n{self.error}"

            response_data = response

            if response_data.get("is_execution_finished", False):
                break
            await asyncio.sleep(2)

        if not response_data or "result" not in response_data:
            return f"*Xchange Volume*\n\n{self.error}"

        try:
            last_24hr_amt = response_data["result"]["rows"][0]["last_24hr_amt"]
            last_30d_amt = response_data["result"]["rows"][0]["last_30d_amt"]
            last_7d_amt = response_data["result"]["rows"][0]["last_7d_amt"]
            lifetime_amt = response_data["result"]["rows"][0]["lifetime_amt"]
        except (KeyError, IndexError):
            return f"*Xchange Volume*\n\n{self.error}"

        volume_text = (
            f"Total:       ${lifetime_amt:,.0f}\n"
            f"30 Day:    ${last_30d_amt:,.0f}\n"
            f"7 Day:      ${last_7d_amt:,.0f}\n"
            f"24 Hour:  ${last_24hr_amt:,.0f}"
        )

        self.volume_timestamp = datetime.now().timestamp()
        self.volume_last_date = datetime.fromtimestamp(
            self.volume_timestamp
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.volume_flag = True
        self.volume_text = volume_text

        return f"*Xchange Trading Volume*\n\n{volume_text}"
