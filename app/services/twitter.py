import os
from datetime import datetime

import httpx
from utils import cache


class Twitter(cache.CachedService):
    def __init__(self):
        token = os.getenv("TWITTER_BEARER_TOKEN")
        self.headers = {"Authorization": f"Bearer {token}"}
        super().__init__()

    async def _get(self, path, params=None):
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://api.x.com/2{path}", headers=self.headers, params=params
            )
            resp.raise_for_status()
            return resp.json()

    async def _get_user_id(self, username):
        data = await self._get(f"/users/by/username/{username}")
        return data.get("data", {}).get("id")

    async def ping(self, cache_ttl=None):
        try:
            data = await self._get("/users/by/username/x7_finance")
            return (
                True
                if data.get("data")
                else "🔴 Twitter: Connection failed (No data returned)"
            )
        except Exception as e:
            return f"🔴 Twitter: Connection failed: {e}"

    async def get_user_data(self, username, cache_ttl=600):
        try:
            data = await self._get(
                f"/users/by/username/{username}",
                params={"user.fields": "public_metrics,profile_image_url"},
            )
            user = data.get("data")
            if user:
                return {
                    "followers": user["public_metrics"]["followers_count"],
                    "profile_image": user.get("profile_image_url"),
                }
            return {"followers": "N/A", "profile_image": None}
        except Exception:
            return {"followers": "N/A", "profile_image": None}

    async def get_latest_tweet(self, username, cache_ttl=300):
        try:
            user_id = await self._get_user_id(username)
            if not user_id:
                return None
            data = await self._get(
                f"/users/{user_id}/tweets",
                params={
                    "max_results": 5,
                    "tweet.fields": "created_at,public_metrics,referenced_tweets",
                },
            )
            tweets = data.get("data")
            if not tweets:
                return None
            tweet = tweets[0]

            refs = tweet.get("referenced_tweets")
            tweet_type = (
                {"replied_to": "Reply", "retweeted": "Retweet", "quoted": "Quote"}.get(
                    refs[0]["type"], "Tweet"
                )
                if refs
                else "Tweet"
            )

            metrics = tweet.get("public_metrics", {})
            created = tweet.get("created_at")
            return {
                "text": tweet["text"],
                "url": f"https://twitter.com/{username}/status/{tweet['id']}",
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "created_at": datetime.fromisoformat(created.replace("Z", "+00:00"))
                if created
                else None,
                "type": tweet_type,
            }
        except Exception:
            return None

    async def get_next_space(self, username, cache_ttl=600):
        try:
            user_id = await self._get_user_id(username)
            if not user_id:
                return None
            data = await self._get(
                "/spaces/by/creator-ids",
                params={
                    "user_ids": user_id,
                    "space.fields": "title,state,scheduled_start",
                },
            )
            for space in data.get("data") or []:
                if space.get("state") in ("live", "scheduled"):
                    return {
                        "title": space.get("title"),
                        "state": "Live Now"
                        if space["state"] == "live"
                        else "Scheduled",
                        "scheduled_start": space.get("scheduled_start"),
                        "space_id": space.get("id"),
                    }
            return None
        except Exception:
            return None
