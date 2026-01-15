"""
A.B.E.L - YouTube Service
YouTube Data API integration
"""

from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.logging import logger


class YouTubeService:
    """
    YouTube Data API integration:
    - Search videos
    - Get video details
    - Manage playlists
    - Get channel info
    - Subscriptions
    """

    SCOPES = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.readonly",
    ]

    def __init__(self, credentials: Credentials = None, api_key: str = None):
        if credentials:
            self.service = build("youtube", "v3", credentials=credentials)
        elif api_key:
            self.service = build("youtube", "v3", developerKey=api_key)
        else:
            raise ValueError("Either credentials or api_key must be provided")

    # ========================================
    # SEARCH
    # ========================================
    async def search(
        self,
        query: str,
        search_type: str = "video",  # video, channel, playlist
        max_results: int = 25,
        order: str = "relevance",  # relevance, date, rating, viewCount
        region_code: str = "FR",
    ) -> List[Dict[str, Any]]:
        """Search YouTube"""
        try:
            results = (
                self.service.search()
                .list(
                    q=query,
                    type=search_type,
                    part="snippet",
                    maxResults=max_results,
                    order=order,
                    regionCode=region_code,
                )
                .execute()
            )
            return results.get("items", [])
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return []

    async def search_videos(
        self,
        query: str,
        max_results: int = 25,
        published_after: Optional[str] = None,
        video_duration: Optional[str] = None,  # short, medium, long
    ) -> List[Dict[str, Any]]:
        """Search for videos with filters"""
        try:
            params = {
                "q": query,
                "type": "video",
                "part": "snippet",
                "maxResults": max_results,
            }
            if published_after:
                params["publishedAfter"] = published_after
            if video_duration:
                params["videoDuration"] = video_duration

            results = self.service.search().list(**params).execute()
            return results.get("items", [])
        except Exception as e:
            logger.error(f"YouTube search videos error: {e}")
            return []

    # ========================================
    # VIDEO OPERATIONS
    # ========================================
    async def get_video(
        self,
        video_id: str,
        parts: str = "snippet,statistics,contentDetails",
    ) -> Optional[Dict[str, Any]]:
        """Get video details"""
        try:
            results = (
                self.service.videos()
                .list(id=video_id, part=parts)
                .execute()
            )
            items = results.get("items", [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"YouTube get video error: {e}")
            return None

    async def get_videos(
        self,
        video_ids: List[str],
        parts: str = "snippet,statistics,contentDetails",
    ) -> List[Dict[str, Any]]:
        """Get multiple videos details"""
        try:
            results = (
                self.service.videos()
                .list(id=",".join(video_ids), part=parts)
                .execute()
            )
            return results.get("items", [])
        except Exception as e:
            logger.error(f"YouTube get videos error: {e}")
            return []

    async def get_trending(
        self,
        region_code: str = "FR",
        category_id: str = "0",  # 0 = all
        max_results: int = 25,
    ) -> List[Dict[str, Any]]:
        """Get trending videos"""
        try:
            results = (
                self.service.videos()
                .list(
                    chart="mostPopular",
                    regionCode=region_code,
                    videoCategoryId=category_id,
                    part="snippet,statistics",
                    maxResults=max_results,
                )
                .execute()
            )
            return results.get("items", [])
        except Exception as e:
            logger.error(f"YouTube get trending error: {e}")
            return []

    # ========================================
    # CHANNEL OPERATIONS
    # ========================================
    async def get_channel(
        self,
        channel_id: str = None,
        username: str = None,
        parts: str = "snippet,statistics,contentDetails",
    ) -> Optional[Dict[str, Any]]:
        """Get channel details"""
        try:
            params = {"part": parts}
            if channel_id:
                params["id"] = channel_id
            elif username:
                params["forUsername"] = username

            results = self.service.channels().list(**params).execute()
            items = results.get("items", [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"YouTube get channel error: {e}")
            return None

    async def get_my_channel(
        self,
        parts: str = "snippet,statistics,contentDetails",
    ) -> Optional[Dict[str, Any]]:
        """Get authenticated user's channel"""
        try:
            results = (
                self.service.channels()
                .list(mine=True, part=parts)
                .execute()
            )
            items = results.get("items", [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"YouTube get my channel error: {e}")
            return None

    async def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 50,
        order: str = "date",
    ) -> List[Dict[str, Any]]:
        """Get videos from a channel"""
        try:
            results = (
                self.service.search()
                .list(
                    channelId=channel_id,
                    type="video",
                    part="snippet",
                    maxResults=max_results,
                    order=order,
                )
                .execute()
            )
            return results.get("items", [])
        except Exception as e:
            logger.error(f"YouTube channel videos error: {e}")
            return []

    # ========================================
    # PLAYLIST OPERATIONS
    # ========================================
    async def list_playlists(
        self,
        channel_id: str = None,
        mine: bool = False,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """List playlists"""
        try:
            params = {
                "part": "snippet,contentDetails",
                "maxResults": max_results,
            }
            if mine:
                params["mine"] = True
            elif channel_id:
                params["channelId"] = channel_id

            results = self.service.playlists().list(**params).execute()
            return results.get("items", [])
        except Exception as e:
            logger.error(f"YouTube list playlists error: {e}")
            return []

    async def get_playlist(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Get playlist details"""
        try:
            results = (
                self.service.playlists()
                .list(id=playlist_id, part="snippet,contentDetails")
                .execute()
            )
            items = results.get("items", [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"YouTube get playlist error: {e}")
            return None

    async def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get videos in a playlist"""
        try:
            items = []
            page_token = None

            while True:
                results = (
                    self.service.playlistItems()
                    .list(
                        playlistId=playlist_id,
                        part="snippet,contentDetails",
                        maxResults=min(max_results - len(items), 50),
                        pageToken=page_token,
                    )
                    .execute()
                )
                items.extend(results.get("items", []))
                page_token = results.get("nextPageToken")
                if not page_token or len(items) >= max_results:
                    break

            return items
        except Exception as e:
            logger.error(f"YouTube playlist items error: {e}")
            return []

    async def create_playlist(
        self,
        title: str,
        description: str = "",
        privacy: str = "private",  # private, public, unlisted
    ) -> Optional[Dict[str, Any]]:
        """Create a playlist"""
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                },
                "status": {"privacyStatus": privacy},
            }
            return (
                self.service.playlists()
                .insert(part="snippet,status", body=body)
                .execute()
            )
        except Exception as e:
            logger.error(f"YouTube create playlist error: {e}")
            return None

    async def add_to_playlist(
        self,
        playlist_id: str,
        video_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Add video to playlist"""
        try:
            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    },
                }
            }
            return (
                self.service.playlistItems()
                .insert(part="snippet", body=body)
                .execute()
            )
        except Exception as e:
            logger.error(f"YouTube add to playlist error: {e}")
            return None

    async def remove_from_playlist(self, playlist_item_id: str) -> bool:
        """Remove video from playlist"""
        try:
            self.service.playlistItems().delete(id=playlist_item_id).execute()
            return True
        except Exception as e:
            logger.error(f"YouTube remove from playlist error: {e}")
            return False

    async def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist"""
        try:
            self.service.playlists().delete(id=playlist_id).execute()
            return True
        except Exception as e:
            logger.error(f"YouTube delete playlist error: {e}")
            return False

    # ========================================
    # SUBSCRIPTIONS
    # ========================================
    async def list_subscriptions(
        self,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """List user's subscriptions"""
        try:
            items = []
            page_token = None

            while True:
                results = (
                    self.service.subscriptions()
                    .list(
                        mine=True,
                        part="snippet",
                        maxResults=min(max_results - len(items), 50),
                        pageToken=page_token,
                    )
                    .execute()
                )
                items.extend(results.get("items", []))
                page_token = results.get("nextPageToken")
                if not page_token or len(items) >= max_results:
                    break

            return items
        except Exception as e:
            logger.error(f"YouTube list subscriptions error: {e}")
            return []

    async def subscribe(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Subscribe to a channel"""
        try:
            body = {
                "snippet": {
                    "resourceId": {
                        "kind": "youtube#channel",
                        "channelId": channel_id,
                    }
                }
            }
            return (
                self.service.subscriptions()
                .insert(part="snippet", body=body)
                .execute()
            )
        except Exception as e:
            logger.error(f"YouTube subscribe error: {e}")
            return None

    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a channel"""
        try:
            self.service.subscriptions().delete(id=subscription_id).execute()
            return True
        except Exception as e:
            logger.error(f"YouTube unsubscribe error: {e}")
            return False

    # ========================================
    # CATEGORIES
    # ========================================
    async def get_video_categories(
        self,
        region_code: str = "FR",
    ) -> List[Dict[str, Any]]:
        """Get video categories"""
        try:
            results = (
                self.service.videoCategories()
                .list(part="snippet", regionCode=region_code)
                .execute()
            )
            return results.get("items", [])
        except Exception as e:
            logger.error(f"YouTube categories error: {e}")
            return []

    # Video Categories IDs
    VIDEO_CATEGORIES = {
        "1": "Film & Animation",
        "2": "Autos & Vehicles",
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "18": "Short Movies",
        "19": "Travel & Events",
        "20": "Gaming",
        "21": "Videoblogging",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "Howto & Style",
        "27": "Education",
        "28": "Science & Technology",
        "29": "Nonprofits & Activism",
    }
