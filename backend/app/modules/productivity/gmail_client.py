"""
A.B.E.L - Gmail Client (Read and manage emails)
"""

import base64
from typing import Optional, List, Dict, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.core.logging import logger


class GmailClient:
    """
    Gmail API client for A.B.E.L.

    Features:
    - Read unread emails
    - Search emails
    - Send emails
    - Mark as read/unread
    - Label management
    """

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        """Initialize Gmail client with OAuth tokens."""
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
        )
        self.service = build("gmail", "v1", credentials=self.credentials)

    async def get_unread_emails(
        self,
        max_results: int = 10,
        label_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get unread emails from inbox.

        Args:
            max_results: Maximum number of emails to return
            label_ids: Filter by label IDs

        Returns:
            List of email dictionaries
        """
        try:
            labels = label_ids or ["INBOX", "UNREAD"]

            # List messages
            results = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=labels,
                    maxResults=max_results,
                )
                .execute()
            )

            messages = results.get("messages", [])
            emails = []

            for msg in messages:
                email_data = await self._get_email_details(msg["id"])
                if email_data:
                    emails.append(email_data)

            logger.info(f"Retrieved {len(emails)} unread emails")
            return emails

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise

    async def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific email."""
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            headers = message.get("payload", {}).get("headers", [])
            header_dict = {h["name"].lower(): h["value"] for h in headers}

            # Extract body
            body = self._extract_body(message.get("payload", {}))

            return {
                "id": message_id,
                "thread_id": message.get("threadId"),
                "subject": header_dict.get("subject", "(No Subject)"),
                "from": header_dict.get("from", "Unknown"),
                "to": header_dict.get("to", ""),
                "date": header_dict.get("date", ""),
                "snippet": message.get("snippet", ""),
                "body": body,
                "labels": message.get("labelIds", []),
                "is_unread": "UNREAD" in message.get("labelIds", []),
            }

        except HttpError as e:
            logger.error(f"Error getting email {message_id}: {e}")
            return None

    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        body = ""

        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        elif "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    if part.get("body", {}).get("data"):
                        body = base64.urlsafe_b64decode(
                            part["body"]["data"]
                        ).decode("utf-8")
                        break
                elif part.get("mimeType") == "text/html" and not body:
                    if part.get("body", {}).get("data"):
                        body = base64.urlsafe_b64decode(
                            part["body"]["data"]
                        ).decode("utf-8")

        return body

    async def search_emails(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search emails using Gmail search syntax.

        Args:
            query: Search query (e.g., "from:user@example.com")
            max_results: Maximum results

        Returns:
            List of matching emails
        """
        try:
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            emails = []

            for msg in messages:
                email_data = await self._get_email_details(msg["id"])
                if email_data:
                    emails.append(email_data)

            return emails

        except HttpError as e:
            logger.error(f"Gmail search error: {e}")
            raise

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> Dict[str, Any]:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML

        Returns:
            Sent message info
        """
        try:
            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject

            msg_type = "html" if html else "plain"
            message.attach(MIMEText(body, msg_type))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            result = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )

            logger.info(f"Email sent to {to}: {subject}")

            return {
                "id": result["id"],
                "thread_id": result["threadId"],
                "status": "sent",
            }

        except HttpError as e:
            logger.error(f"Error sending email: {e}")
            raise

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read."""
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            return True
        except HttpError as e:
            logger.error(f"Error marking email as read: {e}")
            return False

    async def mark_as_unread(self, message_id: str) -> bool:
        """Mark an email as unread."""
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"addLabelIds": ["UNREAD"]},
            ).execute()
            return True
        except HttpError as e:
            logger.error(f"Error marking email as unread: {e}")
            return False

    async def get_labels(self) -> List[Dict[str, str]]:
        """Get all Gmail labels."""
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            return [{"id": l["id"], "name": l["name"]} for l in labels]
        except HttpError as e:
            logger.error(f"Error getting labels: {e}")
            return []
