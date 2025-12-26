"""
A.B.E.L - Instagram Client (via instagrapi)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from instagrapi import Client as InstaClient
from instagrapi.types import DirectThread, DirectMessage

from app.core.config import settings
from app.core.logging import logger


class InstagramClient:
    """
    Instagram client using instagrapi.

    Features:
    - Read DMs
    - Send DMs
    - Get conversation history
    - Post stories/posts (if needed)
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        session_data: Optional[str] = None,
    ):
        """Initialize Instagram client."""
        self.username = username or settings.instagram_username
        self.password = password or settings.instagram_password
        self.client = InstaClient()
        self._logged_in = False

        if session_data:
            try:
                self.client.set_settings(eval(session_data))
                self._logged_in = True
            except Exception:
                pass

    async def login(self) -> bool:
        """
        Login to Instagram.

        Returns:
            True if login successful
        """
        try:
            if self._logged_in:
                return True

            if not self.username or not self.password:
                logger.error("Instagram credentials not configured")
                return False

            self.client.login(self.username, self.password)
            self._logged_in = True
            logger.info(f"Logged in to Instagram as {self.username}")
            return True

        except Exception as e:
            logger.error(f"Instagram login error: {e}")
            return False

    def get_session_data(self) -> str:
        """Get session data for persistence."""
        return str(self.client.get_settings())

    async def get_direct_threads(
        self,
        amount: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get direct message threads.

        Args:
            amount: Number of threads to retrieve

        Returns:
            List of conversation threads
        """
        try:
            if not self._logged_in:
                await self.login()

            threads = self.client.direct_threads(amount=amount)

            return [
                {
                    "thread_id": thread.id,
                    "thread_title": thread.thread_title,
                    "users": [
                        {
                            "pk": user.pk,
                            "username": user.username,
                            "full_name": user.full_name,
                            "profile_pic_url": str(user.profile_pic_url) if user.profile_pic_url else None,
                        }
                        for user in thread.users
                    ],
                    "last_activity_at": thread.last_activity_at.isoformat() if thread.last_activity_at else None,
                    "is_group": thread.is_group,
                    "unread_count": thread.read_state,
                }
                for thread in threads
            ]

        except Exception as e:
            logger.error(f"Error getting DM threads: {e}")
            return []

    async def get_thread_messages(
        self,
        thread_id: str,
        amount: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a specific thread.

        Args:
            thread_id: Thread ID
            amount: Number of messages

        Returns:
            List of messages
        """
        try:
            if not self._logged_in:
                await self.login()

            thread = self.client.direct_thread(thread_id, amount=amount)

            messages = []
            for msg in thread.messages:
                message_data = {
                    "id": msg.id,
                    "user_id": msg.user_id,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "item_type": msg.item_type,
                }

                if msg.item_type == "text":
                    message_data["text"] = msg.text
                elif msg.item_type == "media":
                    message_data["media_url"] = str(msg.media.url) if msg.media else None
                elif msg.item_type == "link":
                    message_data["link"] = msg.link.url if msg.link else None

                messages.append(message_data)

            return messages

        except Exception as e:
            logger.error(f"Error getting thread messages: {e}")
            return []

    async def send_direct_message(
        self,
        user_ids: List[int],
        text: str,
        thread_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a direct message.

        Args:
            user_ids: List of user IDs to send to
            text: Message text
            thread_id: Existing thread ID (optional)

        Returns:
            Sent message info
        """
        try:
            if not self._logged_in:
                await self.login()

            if thread_id:
                result = self.client.direct_send(text, thread_ids=[thread_id])
            else:
                result = self.client.direct_send(text, user_ids=user_ids)

            logger.info(f"Sent DM to {user_ids}: {text[:50]}...")

            return {
                "status": "sent",
                "thread_id": result.thread_id if hasattr(result, 'thread_id') else None,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error sending DM: {e}")
            return None

    async def get_conversation_context(
        self,
        thread_id: str,
        message_count: int = 10,
    ) -> Dict[str, Any]:
        """
        Get full conversation context for analysis.

        Args:
            thread_id: Thread ID
            message_count: Number of recent messages

        Returns:
            Conversation context with messages and user info
        """
        try:
            if not self._logged_in:
                await self.login()

            thread = self.client.direct_thread(thread_id, amount=message_count)

            # Build context
            messages_text = []
            for msg in reversed(thread.messages):
                if msg.item_type == "text" and msg.text:
                    # Get username for this message
                    user = next(
                        (u for u in thread.users if u.pk == msg.user_id),
                        None
                    )
                    username = user.username if user else "unknown"

                    if msg.user_id == self.client.user_id:
                        messages_text.append(f"Moi: {msg.text}")
                    else:
                        messages_text.append(f"{username}: {msg.text}")

            return {
                "thread_id": thread_id,
                "participants": [
                    {
                        "pk": user.pk,
                        "username": user.username,
                        "full_name": user.full_name,
                    }
                    for user in thread.users
                ],
                "messages": messages_text,
                "conversation_text": "\n".join(messages_text),
                "last_message": messages_text[-1] if messages_text else None,
                "message_count": len(messages_text),
            }

        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {}

    async def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get Instagram user info."""
        try:
            if not self._logged_in:
                await self.login()

            user = self.client.user_info_by_username(username)

            return {
                "pk": user.pk,
                "username": user.username,
                "full_name": user.full_name,
                "biography": user.biography,
                "follower_count": user.follower_count,
                "following_count": user.following_count,
                "media_count": user.media_count,
                "is_private": user.is_private,
                "is_verified": user.is_verified,
                "profile_pic_url": str(user.profile_pic_url) if user.profile_pic_url else None,
            }

        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None

    async def mark_thread_as_read(self, thread_id: str) -> bool:
        """Mark a thread as read."""
        try:
            if not self._logged_in:
                await self.login()

            self.client.direct_thread_mark_as_seen(thread_id)
            return True

        except Exception as e:
            logger.error(f"Error marking thread as read: {e}")
            return False
