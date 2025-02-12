import requests


class Snapshot:
    def __init__(self):
        self.url = "https://hub.snapshot.org/graphql"

    def ping(self):
        try:
            query = {"query": "query { proposals(first: 1) { id } }"}
            response = requests.post(self.url, json=query, timeout=5)
            if response.status_code == 200:
                return True
            return f"🔴 Snapshot: Connection failed: {response.status_code} {response.text}"
        except requests.RequestException as e:
            return f"🔴 Snapshot: Connection failed: {e}"

    def get_latest(self):
        query = {
            "query": 'query { proposals ( first: 1, skip: 0, where: { space_in: ["x7finance.eth"]}, '
            'orderBy: "created", orderDirection: desc ) { id title start end snapshot state choices '
            "scores scores_total author }}"
        }
        response = requests.get(self.url, query)
        return response.json()
