"""
A.B.E.L - Google Sheets Service
Spreadsheet manipulation and data analysis
"""

from typing import Optional, List, Dict, Any, Union
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.logging import logger


class SheetsService:
    """
    Google Sheets integration:
    - Create spreadsheets
    - Read/write cells
    - Format cells
    - Charts
    - Data analysis
    """

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    def __init__(self, credentials: Credentials):
        self.service = build("sheets", "v4", credentials=credentials)

    # ========================================
    # SPREADSHEET OPERATIONS
    # ========================================
    async def create_spreadsheet(
        self,
        title: str,
        sheet_names: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new spreadsheet"""
        try:
            sheets = []
            if sheet_names:
                sheets = [{"properties": {"title": name}} for name in sheet_names]
            else:
                sheets = [{"properties": {"title": "Sheet1"}}]

            spreadsheet = {
                "properties": {"title": title},
                "sheets": sheets,
            }

            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            return {
                "id": result.get("spreadsheetId"),
                "title": result.get("properties", {}).get("title"),
                "url": result.get("spreadsheetUrl"),
                "sheets": [
                    s.get("properties", {}).get("title")
                    for s in result.get("sheets", [])
                ],
            }
        except Exception as e:
            logger.error(f"Sheets create error: {e}")
            return None

    async def get_spreadsheet(self, spreadsheet_id: str) -> Optional[Dict[str, Any]]:
        """Get spreadsheet metadata"""
        try:
            result = (
                self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Sheets get error: {e}")
            return None

    # ========================================
    # CELL OPERATIONS
    # ========================================
    async def read_range(
        self,
        spreadsheet_id: str,
        range_name: str,
    ) -> List[List[Any]]:
        """Read values from a range"""
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            return result.get("values", [])
        except Exception as e:
            logger.error(f"Sheets read error: {e}")
            return []

    async def write_range(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        value_input_option: str = "USER_ENTERED",
    ) -> bool:
        """Write values to a range"""
        try:
            body = {"values": values}
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets write error: {e}")
            return False

    async def append_rows(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
    ) -> bool:
        """Append rows to a sheet"""
        try:
            body = {"values": values}
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets append error: {e}")
            return False

    async def clear_range(
        self,
        spreadsheet_id: str,
        range_name: str,
    ) -> bool:
        """Clear values from a range"""
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id, range=range_name
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets clear error: {e}")
            return False

    async def batch_read(
        self,
        spreadsheet_id: str,
        ranges: List[str],
    ) -> Dict[str, List[List[Any]]]:
        """Read multiple ranges at once"""
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .batchGet(spreadsheetId=spreadsheet_id, ranges=ranges)
                .execute()
            )
            value_ranges = result.get("valueRanges", [])
            return {
                vr.get("range"): vr.get("values", [])
                for vr in value_ranges
            }
        except Exception as e:
            logger.error(f"Sheets batch read error: {e}")
            return {}

    async def batch_write(
        self,
        spreadsheet_id: str,
        data: Dict[str, List[List[Any]]],
    ) -> bool:
        """Write to multiple ranges at once"""
        try:
            value_ranges = [
                {"range": range_name, "values": values}
                for range_name, values in data.items()
            ]
            body = {"valueInputOption": "USER_ENTERED", "data": value_ranges}
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets batch write error: {e}")
            return False

    # ========================================
    # SHEET MANAGEMENT
    # ========================================
    async def add_sheet(
        self,
        spreadsheet_id: str,
        title: str,
        rows: int = 1000,
        cols: int = 26,
    ) -> Optional[int]:
        """Add a new sheet"""
        try:
            requests = [
                {
                    "addSheet": {
                        "properties": {
                            "title": title,
                            "gridProperties": {
                                "rowCount": rows,
                                "columnCount": cols,
                            },
                        }
                    }
                }
            ]
            result = (
                self.service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests})
                .execute()
            )
            return result.get("replies", [{}])[0].get("addSheet", {}).get(
                "properties", {}
            ).get("sheetId")
        except Exception as e:
            logger.error(f"Sheets add sheet error: {e}")
            return None

    async def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> bool:
        """Delete a sheet"""
        try:
            requests = [{"deleteSheet": {"sheetId": sheet_id}}]
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets delete sheet error: {e}")
            return False

    async def rename_sheet(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        new_title: str,
    ) -> bool:
        """Rename a sheet"""
        try:
            requests = [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": sheet_id, "title": new_title},
                        "fields": "title",
                    }
                }
            ]
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets rename error: {e}")
            return False

    # ========================================
    # FORMATTING
    # ========================================
    async def format_cells(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        start_col: int,
        end_col: int,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        font_size: Optional[int] = None,
        background_color: Optional[Dict[str, float]] = None,
        text_color: Optional[Dict[str, float]] = None,
    ) -> bool:
        """Format a range of cells"""
        try:
            cell_format = {}

            if bold is not None or italic is not None or font_size is not None:
                cell_format["textFormat"] = {}
                if bold is not None:
                    cell_format["textFormat"]["bold"] = bold
                if italic is not None:
                    cell_format["textFormat"]["italic"] = italic
                if font_size is not None:
                    cell_format["textFormat"]["fontSize"] = font_size

            if background_color:
                cell_format["backgroundColor"] = background_color

            if text_color:
                if "textFormat" not in cell_format:
                    cell_format["textFormat"] = {}
                cell_format["textFormat"]["foregroundColor"] = text_color

            requests = [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        },
                        "cell": {"userEnteredFormat": cell_format},
                        "fields": "userEnteredFormat",
                    }
                }
            ]
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets format error: {e}")
            return False

    async def auto_resize_columns(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_col: int = 0,
        end_col: int = 26,
    ) -> bool:
        """Auto-resize columns to fit content"""
        try:
            requests = [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": start_col,
                            "endIndex": end_col,
                        }
                    }
                }
            ]
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets auto resize error: {e}")
            return False

    # ========================================
    # DATA OPERATIONS
    # ========================================
    async def sort_range(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        start_col: int,
        end_col: int,
        sort_col: int,
        ascending: bool = True,
    ) -> bool:
        """Sort a range by column"""
        try:
            requests = [
                {
                    "sortRange": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row,
                            "endRowIndex": end_row,
                            "startColumnIndex": start_col,
                            "endColumnIndex": end_col,
                        },
                        "sortSpecs": [
                            {
                                "dimensionIndex": sort_col,
                                "sortOrder": "ASCENDING" if ascending else "DESCENDING",
                            }
                        ],
                    }
                }
            ]
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets sort error: {e}")
            return False

    async def add_filter(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        start_col: int,
        end_col: int,
    ) -> bool:
        """Add a filter to a range"""
        try:
            requests = [
                {
                    "setBasicFilter": {
                        "filter": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": start_row,
                                "endRowIndex": end_row,
                                "startColumnIndex": start_col,
                                "endColumnIndex": end_col,
                            }
                        }
                    }
                }
            ]
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets filter error: {e}")
            return False

    # ========================================
    # CHARTS
    # ========================================
    async def add_chart(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        chart_type: str,  # BAR, LINE, PIE, COLUMN, AREA, SCATTER
        data_range: str,
        title: str,
        position: Dict[str, int],  # {"row": 0, "col": 5}
    ) -> bool:
        """Add a chart"""
        try:
            chart_types = {
                "BAR": "BAR",
                "LINE": "LINE",
                "PIE": "PIE",
                "COLUMN": "COLUMN",
                "AREA": "AREA",
                "SCATTER": "SCATTER",
            }

            requests = [
                {
                    "addChart": {
                        "chart": {
                            "spec": {
                                "title": title,
                                "basicChart": {
                                    "chartType": chart_types.get(chart_type.upper(), "LINE"),
                                    "legendPosition": "BOTTOM_LEGEND",
                                    "domains": [
                                        {
                                            "domain": {
                                                "sourceRange": {
                                                    "sources": [
                                                        {"sheetId": sheet_id}
                                                    ]
                                                }
                                            }
                                        }
                                    ],
                                },
                            },
                            "position": {
                                "overlayPosition": {
                                    "anchorCell": {
                                        "sheetId": sheet_id,
                                        "rowIndex": position.get("row", 0),
                                        "columnIndex": position.get("col", 5),
                                    }
                                }
                            },
                        }
                    }
                }
            ]
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": requests}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Sheets add chart error: {e}")
            return False

    # ========================================
    # HELPER METHODS
    # ========================================
    def column_letter_to_index(self, letter: str) -> int:
        """Convert column letter to index (A=0, B=1, etc.)"""
        result = 0
        for char in letter.upper():
            result = result * 26 + (ord(char) - ord("A") + 1)
        return result - 1

    def index_to_column_letter(self, index: int) -> str:
        """Convert index to column letter (0=A, 1=B, etc.)"""
        result = ""
        while index >= 0:
            result = chr(index % 26 + ord("A")) + result
            index = index // 26 - 1
        return result
