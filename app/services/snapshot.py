import aiohttp


class Snapshot:
    def __init__(self):
        self.url = "https://hub.snapshot.org/graphql"

    async def ping(self):
        try:
            query = {"query": "query { proposals(first: 1) { id } }"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, json=query, timeout=5
                ) as response:
                    if response.status == 200:
                        return True
                    return f"🔴 Snapshot: Connection failed: {response.status} {await response.text()}"
        except Exception as e:
            return f"🔴 Snapshot: Connection failed: {e}"

    async def get_latest(self):
        query = {
            "query": 'query { proposals ( first: 1, skip: 0, where: { space_in: ["x7finance.eth"]}, '
            'orderBy: "created", orderDirection: desc ) { id title start end snapshot state choices '
            "scores scores_total author }}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=query) as response:
                return await response.json()
