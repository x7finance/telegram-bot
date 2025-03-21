import aiohttp
import os
from datetime import datetime

from utils import tools


class GitHub:
    def __init__(self):
        self.url = "https://api.github.com/repos/x7finance/"
        self.headers = {"Authorization": f"token {os.getenv('GITHUB_PAT')}"}

    async def ping(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url + "monorepo", headers=self.headers, timeout=5
                ) as response:
                    if response.status == 200:
                        return True
                    return f"🔴 GitHub: Connection failed: {response.status} {await response.text()}"
        except Exception as e:
            return f"🔴 GitHub: Connection failed: {e}"

    async def get_contributors(self, repo):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url + repo + "/contributors",
                headers=self.headers,
                params={"per_page": 100},
            ) as response:
                if response.status != 200:
                    return f"Error fetching contributors: {response.status}"

                contributors = await response.json()
                return len(contributors)

    async def get_issues(self, repo):
        endpoint = "/issues"
        issues = []
        page = 1

        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                    self.url + repo + endpoint,
                    headers=self.headers,
                    params={"state": "open", "page": page, "per_page": 100},
                ) as response:
                    if response.status != 200:
                        break

                    data = await response.json()
                    if not data:
                        break

                    issues.extend(
                        [
                            issue
                            for issue in data
                            if "pull_request" not in issue
                        ]
                    )
                    page += 1

        if not issues:
            return "No open issues found."

        formatted_issues = []
        for issue in issues:
            title = issue.get("title", "No Title")
            creator = issue.get("user", {}).get("login", "Unknown")
            created_at = issue.get("created_at", "Unknown")
            labels = ", ".join(
                [label.get("name", "") for label in issue.get("labels", [])]
            )
            url = issue.get("html_url", "No URL")

            if created_at != "Unknown":
                created_at = datetime.fromisoformat(
                    created_at.replace("Z", "")
                ).strftime("%Y-%m-%d %H:%M:%S")

            formatted_issues.append(
                f"{title} ({labels})\n"
                f"Creator: {creator}\n"
                f"Created At: {created_at}\n"
                f"URL: {url}\n"
            )

        issue_count = len(issues)
        return f"Total Open Issues: {issue_count}\n\n" + "\n".join(
            formatted_issues
        )

    async def get_latest_commit(self, repo):
        endpoint = "/commits"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url + repo + endpoint, headers=self.headers
            ) as response:
                if response.status != 200:
                    return f"Error fetching commits: {response.status}, {await response.text()}"

                commits = await response.json()
                if not commits:
                    return "No commits found."

                latest_commit = commits[0]
                message = tools.escape_markdown(
                    latest_commit.get("commit", {}).get(
                        "message", "No message"
                    )
                )
                created_by = tools.escape_markdown(
                    latest_commit.get("commit", {})
                    .get("author", {})
                    .get("name", "Unknown author")
                )
                created_at = (
                    latest_commit.get("commit", {})
                    .get("author", {})
                    .get("date", "Unknown date")
                )
                url = latest_commit.get("html_url", "No URL")

                if created_at != "Unknown":
                    created_at = datetime.fromisoformat(
                        created_at.replace("Z", "")
                    ).strftime("%Y-%m-%d %H:%M:%S")

                return f"Latest Commit:\n{message}\nCreated By: {created_by}\nCreated At: {created_at}\nURL: {url}"

    async def get_pull_requests(self, repo):
        endpoint = "/pulls"
        pull_requests = []
        page = 1

        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                    self.url + repo + endpoint,
                    headers=self.headers,
                    params={"state": "open", "page": page, "per_page": 100},
                ) as response:
                    if response.status != 200:
                        break

                    data = await response.json()
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
                date = datetime.fromisoformat(date.replace("Z", "")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            formatted_prs.append(
                f"{title}\nCreator: {creator}\nCreated At: {date}\nURL: {url}\n"
            )

        count = len(pull_requests)
        return f"Total Open Pull Requests: {count}\n\n" + "\n".join(
            formatted_prs
        )
