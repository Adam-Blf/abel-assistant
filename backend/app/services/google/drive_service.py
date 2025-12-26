"""
A.B.E.L - Google Drive Service
File storage, sharing, and management
"""

from typing import Optional, List, Dict, Any, BinaryIO
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from app.core.logging import logger


class DriveService:
    """
    Google Drive integration:
    - File upload/download
    - Folder management
    - File sharing
    - Search files
    - Trash management
    """

    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
    ]

    MIME_TYPES = {
        "folder": "application/vnd.google-apps.folder",
        "document": "application/vnd.google-apps.document",
        "spreadsheet": "application/vnd.google-apps.spreadsheet",
        "presentation": "application/vnd.google-apps.presentation",
        "form": "application/vnd.google-apps.form",
        "pdf": "application/pdf",
        "txt": "text/plain",
        "html": "text/html",
        "csv": "text/csv",
        "json": "application/json",
        "zip": "application/zip",
        "jpg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "mp3": "audio/mpeg",
        "mp4": "video/mp4",
    }

    def __init__(self, credentials: Credentials):
        self.service = build("drive", "v3", credentials=credentials)

    # ========================================
    # FILE OPERATIONS
    # ========================================
    async def list_files(
        self,
        query: Optional[str] = None,
        page_size: int = 100,
        order_by: str = "modifiedTime desc",
        fields: str = "files(id, name, mimeType, size, modifiedTime, parents, webViewLink)",
    ) -> List[Dict[str, Any]]:
        """List files in Drive"""
        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    orderBy=order_by,
                    fields=f"nextPageToken, {fields}",
                )
                .execute()
            )
            return results.get("files", [])
        except Exception as e:
            logger.error(f"Drive list error: {e}")
            return []

    async def search_files(
        self,
        name: Optional[str] = None,
        mime_type: Optional[str] = None,
        folder_id: Optional[str] = None,
        trashed: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search files with various criteria"""
        query_parts = []

        if name:
            query_parts.append(f"name contains '{name}'")
        if mime_type:
            query_parts.append(f"mimeType = '{mime_type}'")
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        query_parts.append(f"trashed = {str(trashed).lower()}")

        query = " and ".join(query_parts)
        return await self.list_files(query=query)

    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        try:
            return (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, mimeType, size, modifiedTime, parents, webViewLink, permissions",
                )
                .execute()
            )
        except Exception as e:
            logger.error(f"Drive get file error: {e}")
            return None

    async def upload_file(
        self,
        file_path: str,
        name: str,
        mime_type: str,
        folder_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Upload a file to Drive"""
        try:
            file_metadata = {"name": name}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
                .execute()
            )
            return file
        except Exception as e:
            logger.error(f"Drive upload error: {e}")
            return None

    async def upload_bytes(
        self,
        content: bytes,
        name: str,
        mime_type: str,
        folder_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Upload bytes content to Drive"""
        try:
            from googleapiclient.http import MediaIoBaseUpload

            file_metadata = {"name": name}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaIoBaseUpload(
                io.BytesIO(content), mimetype=mime_type, resumable=True
            )
            file = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
                .execute()
            )
            return file
        except Exception as e:
            logger.error(f"Drive upload bytes error: {e}")
            return None

    async def download_file(self, file_id: str) -> Optional[bytes]:
        """Download file content"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            return file_buffer.getvalue()
        except Exception as e:
            logger.error(f"Drive download error: {e}")
            return None

    async def export_file(
        self,
        file_id: str,
        mime_type: str = "application/pdf",
    ) -> Optional[bytes]:
        """Export Google Docs/Sheets/Slides to another format"""
        try:
            request = self.service.files().export_media(
                fileId=file_id, mimeType=mime_type
            )
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            return file_buffer.getvalue()
        except Exception as e:
            logger.error(f"Drive export error: {e}")
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file permanently"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            logger.error(f"Drive delete error: {e}")
            return False

    async def trash_file(self, file_id: str) -> bool:
        """Move file to trash"""
        try:
            self.service.files().update(
                fileId=file_id, body={"trashed": True}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Drive trash error: {e}")
            return False

    async def restore_file(self, file_id: str) -> bool:
        """Restore file from trash"""
        try:
            self.service.files().update(
                fileId=file_id, body={"trashed": False}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Drive restore error: {e}")
            return False

    async def rename_file(self, file_id: str, new_name: str) -> bool:
        """Rename a file"""
        try:
            self.service.files().update(
                fileId=file_id, body={"name": new_name}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Drive rename error: {e}")
            return False

    async def move_file(self, file_id: str, new_folder_id: str) -> bool:
        """Move file to another folder"""
        try:
            file = self.service.files().get(
                fileId=file_id, fields="parents"
            ).execute()
            previous_parents = ",".join(file.get("parents", []))

            self.service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=previous_parents,
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Drive move error: {e}")
            return False

    async def copy_file(
        self,
        file_id: str,
        new_name: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Copy a file"""
        try:
            body = {}
            if new_name:
                body["name"] = new_name
            if folder_id:
                body["parents"] = [folder_id]

            return (
                self.service.files()
                .copy(fileId=file_id, body=body, fields="id, name, webViewLink")
                .execute()
            )
        except Exception as e:
            logger.error(f"Drive copy error: {e}")
            return None

    # ========================================
    # FOLDER OPERATIONS
    # ========================================
    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a folder"""
        try:
            file_metadata = {
                "name": name,
                "mimeType": self.MIME_TYPES["folder"],
            }
            if parent_id:
                file_metadata["parents"] = [parent_id]

            return (
                self.service.files()
                .create(body=file_metadata, fields="id, name, webViewLink")
                .execute()
            )
        except Exception as e:
            logger.error(f"Drive create folder error: {e}")
            return None

    async def list_folder(self, folder_id: str = "root") -> List[Dict[str, Any]]:
        """List contents of a folder"""
        return await self.search_files(folder_id=folder_id)

    # ========================================
    # SHARING
    # ========================================
    async def share_file(
        self,
        file_id: str,
        email: str,
        role: str = "reader",  # reader, writer, commenter, owner
        send_notification: bool = True,
    ) -> bool:
        """Share file with specific user"""
        try:
            permission = {"type": "user", "role": role, "emailAddress": email}
            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=send_notification,
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Drive share error: {e}")
            return False

    async def share_public(
        self,
        file_id: str,
        role: str = "reader",
    ) -> Optional[str]:
        """Make file public and return link"""
        try:
            permission = {"type": "anyone", "role": role}
            self.service.permissions().create(
                fileId=file_id, body=permission
            ).execute()

            file = self.service.files().get(
                fileId=file_id, fields="webViewLink"
            ).execute()
            return file.get("webViewLink")
        except Exception as e:
            logger.error(f"Drive share public error: {e}")
            return None

    async def get_permissions(self, file_id: str) -> List[Dict[str, Any]]:
        """Get file permissions"""
        try:
            results = self.service.permissions().list(fileId=file_id).execute()
            return results.get("permissions", [])
        except Exception as e:
            logger.error(f"Drive get permissions error: {e}")
            return []

    async def remove_permission(self, file_id: str, permission_id: str) -> bool:
        """Remove a permission"""
        try:
            self.service.permissions().delete(
                fileId=file_id, permissionId=permission_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Drive remove permission error: {e}")
            return False

    # ========================================
    # STORAGE INFO
    # ========================================
    async def get_storage_quota(self) -> Dict[str, Any]:
        """Get storage quota information"""
        try:
            about = self.service.about().get(fields="storageQuota, user").execute()
            quota = about.get("storageQuota", {})
            return {
                "limit": int(quota.get("limit", 0)),
                "usage": int(quota.get("usage", 0)),
                "usage_in_drive": int(quota.get("usageInDrive", 0)),
                "usage_in_trash": int(quota.get("usageInDriveTrash", 0)),
                "user": about.get("user", {}),
            }
        except Exception as e:
            logger.error(f"Drive quota error: {e}")
            return {}

    # ========================================
    # RECENT & STARRED
    # ========================================
    async def get_recent_files(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently modified files"""
        return await self.list_files(
            query="trashed = false",
            page_size=limit,
            order_by="modifiedTime desc",
        )

    async def get_starred_files(self) -> List[Dict[str, Any]]:
        """Get starred files"""
        return await self.list_files(query="starred = true and trashed = false")

    async def star_file(self, file_id: str, starred: bool = True) -> bool:
        """Star or unstar a file"""
        try:
            self.service.files().update(
                fileId=file_id, body={"starred": starred}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Drive star error: {e}")
            return False
