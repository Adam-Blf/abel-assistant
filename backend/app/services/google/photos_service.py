"""
A.B.E.L - Google Photos Service
Photo library management
"""

from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.logging import logger


class PhotosService:
    """
    Google Photos integration:
    - List albums
    - Search photos
    - Upload photos
    - Create albums
    - Share albums
    """

    SCOPES = [
        "https://www.googleapis.com/auth/photoslibrary",
        "https://www.googleapis.com/auth/photoslibrary.readonly",
        "https://www.googleapis.com/auth/photoslibrary.sharing",
    ]

    def __init__(self, credentials: Credentials):
        self.service = build(
            "photoslibrary", "v1", credentials=credentials, static_discovery=False
        )

    # ========================================
    # ALBUM OPERATIONS
    # ========================================
    async def list_albums(self, page_size: int = 50) -> List[Dict[str, Any]]:
        """List all albums"""
        try:
            albums = []
            page_token = None

            while True:
                results = (
                    self.service.albums()
                    .list(pageSize=page_size, pageToken=page_token)
                    .execute()
                )
                albums.extend(results.get("albums", []))
                page_token = results.get("nextPageToken")
                if not page_token:
                    break

            return albums
        except Exception as e:
            logger.error(f"Photos list albums error: {e}")
            return []

    async def get_album(self, album_id: str) -> Optional[Dict[str, Any]]:
        """Get album details"""
        try:
            return self.service.albums().get(albumId=album_id).execute()
        except Exception as e:
            logger.error(f"Photos get album error: {e}")
            return None

    async def create_album(self, title: str) -> Optional[Dict[str, Any]]:
        """Create a new album"""
        try:
            album = {"album": {"title": title}}
            return self.service.albums().create(body=album).execute()
        except Exception as e:
            logger.error(f"Photos create album error: {e}")
            return None

    async def share_album(
        self,
        album_id: str,
        is_collaborative: bool = False,
        is_commentable: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Share an album"""
        try:
            share_info = {
                "sharedAlbumOptions": {
                    "isCollaborative": is_collaborative,
                    "isCommentable": is_commentable,
                }
            }
            return (
                self.service.albums()
                .share(albumId=album_id, body=share_info)
                .execute()
            )
        except Exception as e:
            logger.error(f"Photos share album error: {e}")
            return None

    async def unshare_album(self, album_id: str) -> bool:
        """Unshare an album"""
        try:
            self.service.albums().unshare(albumId=album_id).execute()
            return True
        except Exception as e:
            logger.error(f"Photos unshare album error: {e}")
            return False

    async def add_to_album(
        self,
        album_id: str,
        media_item_ids: List[str],
    ) -> bool:
        """Add media items to album"""
        try:
            body = {"mediaItemIds": media_item_ids}
            self.service.albums().batchAddMediaItems(
                albumId=album_id, body=body
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Photos add to album error: {e}")
            return False

    async def remove_from_album(
        self,
        album_id: str,
        media_item_ids: List[str],
    ) -> bool:
        """Remove media items from album"""
        try:
            body = {"mediaItemIds": media_item_ids}
            self.service.albums().batchRemoveMediaItems(
                albumId=album_id, body=body
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Photos remove from album error: {e}")
            return False

    # ========================================
    # MEDIA ITEM OPERATIONS
    # ========================================
    async def list_media_items(
        self,
        page_size: int = 100,
        album_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List media items (optionally from specific album)"""
        try:
            items = []
            page_token = None

            if album_id:
                while True:
                    body = {
                        "albumId": album_id,
                        "pageSize": page_size,
                    }
                    if page_token:
                        body["pageToken"] = page_token

                    results = self.service.mediaItems().search(body=body).execute()
                    items.extend(results.get("mediaItems", []))
                    page_token = results.get("nextPageToken")
                    if not page_token:
                        break
            else:
                while True:
                    results = (
                        self.service.mediaItems()
                        .list(pageSize=page_size, pageToken=page_token)
                        .execute()
                    )
                    items.extend(results.get("mediaItems", []))
                    page_token = results.get("nextPageToken")
                    if not page_token:
                        break

            return items
        except Exception as e:
            logger.error(f"Photos list media items error: {e}")
            return []

    async def get_media_item(self, media_item_id: str) -> Optional[Dict[str, Any]]:
        """Get media item details"""
        try:
            return (
                self.service.mediaItems()
                .get(mediaItemId=media_item_id)
                .execute()
            )
        except Exception as e:
            logger.error(f"Photos get media item error: {e}")
            return None

    async def search_media_items(
        self,
        date_filter: Optional[Dict[str, Any]] = None,
        content_filter: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search media items with filters"""
        try:
            items = []
            page_token = None

            body = {"pageSize": page_size}
            filters = {}

            if date_filter:
                filters["dateFilter"] = date_filter
            if content_filter:
                filters["contentFilter"] = content_filter

            if filters:
                body["filters"] = filters

            while True:
                if page_token:
                    body["pageToken"] = page_token

                results = self.service.mediaItems().search(body=body).execute()
                items.extend(results.get("mediaItems", []))
                page_token = results.get("nextPageToken")
                if not page_token:
                    break

            return items
        except Exception as e:
            logger.error(f"Photos search error: {e}")
            return []

    async def search_by_date_range(
        self,
        start_date: Dict[str, int],  # {"year": 2024, "month": 1, "day": 1}
        end_date: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """Search photos by date range"""
        date_filter = {
            "ranges": [
                {
                    "startDate": start_date,
                    "endDate": end_date,
                }
            ]
        }
        return await self.search_media_items(date_filter=date_filter)

    async def search_by_category(
        self,
        categories: List[str],  # ANIMALS, CITYSCAPES, LANDMARKS, etc.
    ) -> List[Dict[str, Any]]:
        """Search photos by content category"""
        content_filter = {"includedContentCategories": categories}
        return await self.search_media_items(content_filter=content_filter)

    # ========================================
    # UPLOAD OPERATIONS
    # ========================================
    async def upload_photo(
        self,
        file_path: str,
        album_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Upload a photo"""
        try:
            import httpx

            # Step 1: Upload bytes to get upload token
            with open(file_path, "rb") as f:
                data = f.read()

            upload_url = "https://photoslibrary.googleapis.com/v1/uploads"
            headers = {
                "Authorization": f"Bearer {self.service._http.credentials.token}",
                "Content-Type": "application/octet-stream",
                "X-Goog-Upload-Content-Type": "image/jpeg",
                "X-Goog-Upload-Protocol": "raw",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    upload_url, headers=headers, content=data, timeout=60.0
                )
                if response.status_code != 200:
                    return None
                upload_token = response.text

            # Step 2: Create media item
            new_item = {
                "simpleMediaItem": {
                    "uploadToken": upload_token,
                }
            }
            if description:
                new_item["description"] = description

            body = {"newMediaItems": [new_item]}
            if album_id:
                body["albumId"] = album_id

            result = self.service.mediaItems().batchCreate(body=body).execute()
            results = result.get("newMediaItemResults", [])

            if results and results[0].get("status", {}).get("message") == "Success":
                return results[0].get("mediaItem")

            return None
        except Exception as e:
            logger.error(f"Photos upload error: {e}")
            return None

    # ========================================
    # CONTENT CATEGORIES
    # ========================================
    CONTENT_CATEGORIES = [
        "ANIMALS",
        "ARTS",
        "BIRTHDAYS",
        "CITYSCAPES",
        "CRAFTS",
        "DOCUMENTS",
        "FASHION",
        "FLOWERS",
        "FOOD",
        "GARDENS",
        "HOLIDAYS",
        "HOUSES",
        "LANDMARKS",
        "LANDSCAPES",
        "NIGHT",
        "PEOPLE",
        "PERFORMANCES",
        "PETS",
        "RECEIPTS",
        "SCREENSHOTS",
        "SELFIES",
        "SPORT",
        "TRAVEL",
        "UTILITY",
        "WEDDINGS",
        "WHITEBOARDS",
    ]
