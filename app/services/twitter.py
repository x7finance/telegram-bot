import os
import tweepy


class Twitter:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN")
        )

    def ping(self):
        try:
            response = self.client.get_user(username="x7_finance")
            if response and response.data:
                return True
            return "🔴 Twitter: Connection failed (No data returned)"
        except tweepy.TweepyException as e:
            return f"🔴 Twitter: Connection failed: {e}"

    def get_user_data(self, username):
        try:
            user = self.client.get_user(
                username=username,
                user_fields=["public_metrics", "profile_image_url"],
            )
            if user and user.data:
                return {
                    "followers": user.data.public_metrics["followers_count"],
                    "profile_image": user.data.profile_image_url,
                }
            return {"followers": "N/A", "profile_image": None}
        except Exception:
            return {"followers": "N/A", "profile_image": None}

    def get_latest_tweet(self, username):
        try:
            user = self.client.get_user(username=username)
            user_id = user.data.id
            tweets = self.client.get_users_tweets(
                user_id,
                max_results=5,
                tweet_fields=[
                    "created_at",
                    "public_metrics",
                    "referenced_tweets",
                ],
            )
            if tweets and tweets.data:
                tweet = tweets.data[0]

                if (
                    hasattr(tweet, "referenced_tweets")
                    and tweet.referenced_tweets
                ):
                    ref_type = tweet.referenced_tweets[0].type
                    if ref_type == "replied_to":
                        tweet_type = "Reply"
                    elif ref_type == "retweeted":
                        tweet_type = "Retweet"
                    elif ref_type == "quoted":
                        tweet_type = "Quote"
                    else:
                        tweet_type = "Tweet"
                else:
                    tweet_type = "Tweet"

                return {
                    "text": tweet.text,
                    "url": f"https://twitter.com/{username}/status/{tweet.id}",
                    "likes": tweet.public_metrics["like_count"],
                    "retweets": tweet.public_metrics["retweet_count"],
                    "replies": tweet.public_metrics.get("reply_count", 0),
                    "created_at": tweet.created_at,
                    "type": tweet_type,
                }
            return None
        except Exception:
            return None

    def get_next_space(self, username):
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return None

            spaces = self.client.get_spaces(
                user_ids=[user_id],
                space_fields=["title", "state", "scheduled_start"],
            )
            if spaces and spaces.data:
                for space in spaces.data:
                    if space.state in ["live", "scheduled"]:
                        return {
                            "title": space.title,
                            "state": (
                                "Live Now"
                                if space.state == "live"
                                else "Scheduled"
                            ),
                            "scheduled_start": getattr(
                                space, "scheduled_start", None
                            ),
                            "space_id": space.id,
                        }
            return None
        except Exception:
            return None
