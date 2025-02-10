import requests


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
