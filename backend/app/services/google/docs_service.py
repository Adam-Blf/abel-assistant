"""
A.B.E.L - Google Docs Service
Document creation and manipulation
"""

from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.logging import logger


class DocsService:
    """
    Google Docs integration:
    - Create documents
    - Read content
    - Insert/update text
    - Format text
    - Insert images
    """

    SCOPES = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/documents.readonly",
    ]

    def __init__(self, credentials: Credentials):
        self.service = build("docs", "v1", credentials=credentials)

    # ========================================
    # DOCUMENT OPERATIONS
    # ========================================
    async def create_document(self, title: str) -> Optional[Dict[str, Any]]:
        """Create a new document"""
        try:
            doc = self.service.documents().create(body={"title": title}).execute()
            return {
                "id": doc.get("documentId"),
                "title": doc.get("title"),
                "url": f"https://docs.google.com/document/d/{doc.get('documentId')}/edit",
            }
        except Exception as e:
            logger.error(f"Docs create error: {e}")
            return None

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata and content"""
        try:
            doc = self.service.documents().get(documentId=document_id).execute()
            return doc
        except Exception as e:
            logger.error(f"Docs get error: {e}")
            return None

    async def get_document_text(self, document_id: str) -> str:
        """Extract plain text from document"""
        try:
            doc = await self.get_document(document_id)
            if not doc:
                return ""

            text = ""
            content = doc.get("body", {}).get("content", [])

            for element in content:
                if "paragraph" in element:
                    for para_element in element["paragraph"].get("elements", []):
                        if "textRun" in para_element:
                            text += para_element["textRun"].get("content", "")

            return text
        except Exception as e:
            logger.error(f"Docs get text error: {e}")
            return ""

    async def insert_text(
        self,
        document_id: str,
        text: str,
        index: int = 1,
    ) -> bool:
        """Insert text at specific index"""
        try:
            requests = [
                {
                    "insertText": {
                        "location": {"index": index},
                        "text": text,
                    }
                }
            ]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Docs insert text error: {e}")
            return False

    async def append_text(self, document_id: str, text: str) -> bool:
        """Append text to end of document"""
        try:
            doc = await self.get_document(document_id)
            if not doc:
                return False

            # Get end index
            end_index = doc.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)

            return await self.insert_text(document_id, text, end_index - 1)
        except Exception as e:
            logger.error(f"Docs append text error: {e}")
            return False

    async def replace_text(
        self,
        document_id: str,
        old_text: str,
        new_text: str,
        match_case: bool = True,
    ) -> bool:
        """Replace text in document"""
        try:
            requests = [
                {
                    "replaceAllText": {
                        "containsText": {
                            "text": old_text,
                            "matchCase": match_case,
                        },
                        "replaceText": new_text,
                    }
                }
            ]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Docs replace text error: {e}")
            return False

    async def insert_paragraph(
        self,
        document_id: str,
        text: str,
        style: str = "NORMAL_TEXT",  # HEADING_1, HEADING_2, etc.
        index: int = 1,
    ) -> bool:
        """Insert a styled paragraph"""
        try:
            requests = [
                {
                    "insertText": {
                        "location": {"index": index},
                        "text": text + "\n",
                    }
                },
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": index,
                            "endIndex": index + len(text) + 1,
                        },
                        "paragraphStyle": {"namedStyleType": style},
                        "fields": "namedStyleType",
                    }
                },
            ]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Docs insert paragraph error: {e}")
            return False

    async def format_text(
        self,
        document_id: str,
        start_index: int,
        end_index: int,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None,
        font_size: Optional[int] = None,
        foreground_color: Optional[Dict[str, float]] = None,
    ) -> bool:
        """Format text range"""
        try:
            text_style = {}
            fields = []

            if bold is not None:
                text_style["bold"] = bold
                fields.append("bold")
            if italic is not None:
                text_style["italic"] = italic
                fields.append("italic")
            if underline is not None:
                text_style["underline"] = underline
                fields.append("underline")
            if font_size is not None:
                text_style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
                fields.append("fontSize")
            if foreground_color is not None:
                text_style["foregroundColor"] = {"color": {"rgbColor": foreground_color}}
                fields.append("foregroundColor")

            requests = [
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start_index,
                            "endIndex": end_index,
                        },
                        "textStyle": text_style,
                        "fields": ",".join(fields),
                    }
                }
            ]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Docs format text error: {e}")
            return False

    async def insert_image(
        self,
        document_id: str,
        image_url: str,
        index: int = 1,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> bool:
        """Insert image from URL"""
        try:
            inline_object = {"uri": image_url}

            if width and height:
                inline_object["objectSize"] = {
                    "width": {"magnitude": width, "unit": "PT"},
                    "height": {"magnitude": height, "unit": "PT"},
                }

            requests = [
                {
                    "insertInlineImage": {
                        "location": {"index": index},
                        "uri": image_url,
                    }
                }
            ]

            if width and height:
                requests[0]["insertInlineImage"]["objectSize"] = {
                    "width": {"magnitude": width, "unit": "PT"},
                    "height": {"magnitude": height, "unit": "PT"},
                }

            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Docs insert image error: {e}")
            return False

    async def insert_table(
        self,
        document_id: str,
        rows: int,
        columns: int,
        index: int = 1,
    ) -> bool:
        """Insert a table"""
        try:
            requests = [
                {
                    "insertTable": {
                        "rows": rows,
                        "columns": columns,
                        "location": {"index": index},
                    }
                }
            ]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Docs insert table error: {e}")
            return False

    async def insert_page_break(self, document_id: str, index: int = 1) -> bool:
        """Insert a page break"""
        try:
            requests = [
                {
                    "insertPageBreak": {
                        "location": {"index": index},
                    }
                }
            ]
            self.service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Docs insert page break error: {e}")
            return False

    async def create_document_from_template(
        self,
        title: str,
        content: str,
    ) -> Optional[Dict[str, Any]]:
        """Create document with initial content"""
        try:
            doc = await self.create_document(title)
            if doc:
                await self.insert_text(doc["id"], content, 1)
                return doc
        except Exception as e:
            logger.error(f"Docs create from template error: {e}")
        return None
