"""
A.B.E.L - Twitter/X Client
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

import tweepy
from tweepy import Client as TwitterAPIClient

from app.core.config import settings
from app.core.logging import logger


class TwitterClient:
    """
    Twitter/X API client for A.B.E.L.

    Features:
    - Post tweets
    - Get timeline
    - Search tweets
    - Analyze trends
    - Reply to mentions
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
    ):
        """Initialize Twitter client."""
        self.api_key = api_key or settings.twitter_api_key
        self.api_secret = api_secret or settings.twitter_api_secret
        self.access_token = access_token or settings.twitter_access_token
        self.access_secret = access_secret or settings.twitter_access_secret
        self.bearer_token = bearer_token or settings.twitter_bearer_token

        # Initialize v2 client
        self.client = TwitterAPIClient(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_secret,
            bearer_token=self.bearer_token,
            wait_on_rate_limit=True,
        )

    async def post_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Post a tweet.

        Args:
            text: Tweet content (max 280 chars)
            reply_to: Tweet ID to reply to
            media_ids: List of media IDs to attach

        Returns:
            Posted tweet info
        """
        try:
            kwargs = {"text": text}

            if reply_to:
                kwargs["in_reply_to_tweet_id"] = reply_to
            if media_ids:
                kwargs["media_ids"] = media_ids

            response = self.client.create_tweet(**kwargs)

            logger.info(f"Posted tweet: {response.data['id']}")

            return {
                "id": response.data["id"],
                "text": text,
                "created_at": datetime.utcnow().isoformat(),
                "status": "posted",
            }

        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            raise

    async def get_timeline(
        self,
        max_results: int = 10,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get home timeline or user tweets.

        Args:
            max_results: Maximum number of tweets
            user_id: Specific user ID (None for home timeline)

        Returns:
            List of tweets
        """
        try:
            if user_id:
                response = self.client.get_users_tweets(
                    id=user_id,
                    max_results=max_results,
                    tweet_fields=["created_at", "public_metrics", "author_id"],
                )
            else:
                response = self.client.get_home_timeline(
                    max_results=max_results,
                    tweet_fields=["created_at", "public_metrics", "author_id"],
                )

            tweets = []
            for tweet in response.data or []:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "metrics": tweet.public_metrics,
                })

            return tweets

        except Exception as e:
            logger.error(f"Error getting timeline: {e}")
            return []

    async def search_tweets(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for tweets.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            List of matching tweets
        """
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "author_id"],
            )

            tweets = []
            for tweet in response.data or []:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "metrics": tweet.public_metrics,
                })

            return tweets

        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []

    async def get_trending_topics(
        self,
        woeid: int = 615702,  # Paris by default
    ) -> List[Dict[str, Any]]:
        """
        Get trending topics.

        Args:
            woeid: Where On Earth ID (615702 = Paris, 1 = Worldwide)

        Returns:
            List of trending topics
        """
        try:
            # Note: This requires v1.1 API access
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_secret,
            )
            api = tweepy.API(auth)

            trends = api.get_place_trends(woeid)

            return [
                {
                    "name": trend["name"],
                    "url": trend["url"],
                    "tweet_volume": trend.get("tweet_volume"),
                    "query": trend["query"],
                }
                for trend in trends[0]["trends"]
            ]

        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return []

    async def get_mentions(
        self,
        max_results: int = 10,
        since_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get mentions of the authenticated user.

        Args:
            max_results: Maximum results
            since_id: Only get mentions after this tweet ID

        Returns:
            List of mention tweets
        """
        try:
            # Get authenticated user ID
            me = self.client.get_me()
            user_id = me.data.id

            kwargs = {
                "id": user_id,
                "max_results": max_results,
                "tweet_fields": ["created_at", "author_id", "in_reply_to_user_id"],
            }

            if since_id:
                kwargs["since_id"] = since_id

            response = self.client.get_users_mentions(**kwargs)

            mentions = []
            for tweet in response.data or []:
                mentions.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                })

            return mentions

        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
            return []

    async def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet."""
        try:
            self.client.like(tweet_id)
            logger.info(f"Liked tweet: {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"Error liking tweet: {e}")
            return False

    async def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet."""
        try:
            self.client.retweet(tweet_id)
            logger.info(f"Retweeted: {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"Error retweeting: {e}")
            return False

    async def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get information about a Twitter user."""
        try:
            response = self.client.get_user(
                username=username,
                user_fields=["description", "public_metrics", "created_at", "profile_image_url"],
            )

            if response.data:
                user = response.data
                return {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name,
                    "description": user.description,
                    "followers_count": user.public_metrics.get("followers_count"),
                    "following_count": user.public_metrics.get("following_count"),
                    "tweet_count": user.public_metrics.get("tweet_count"),
                    "profile_image_url": user.profile_image_url,
                }

            return None

        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
