"""
A.B.E.L - Google Calendar Client
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pytz

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.core.logging import logger


class CalendarClient:
    """
    Google Calendar API client for A.B.E.L.

    Features:
    - List today's events
    - Get upcoming events
    - Create events
    - Update events
    - Delete events
    """

    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        """Initialize Calendar client with OAuth tokens."""
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
        )
        self.service = build("calendar", "v3", credentials=self.credentials)
        self.timezone = pytz.timezone("Europe/Paris")

    async def get_today_events(
        self,
        calendar_id: str = "primary",
    ) -> List[Dict[str, Any]]:
        """
        Get all events for today.

        Returns:
            List of today's events
        """
        try:
            now = datetime.now(self.timezone)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=start_of_day.isoformat(),
                    timeMax=end_of_day.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            return [self._format_event(e) for e in events]

        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            raise

    async def get_upcoming_events(
        self,
        max_results: int = 10,
        days_ahead: int = 7,
        calendar_id: str = "primary",
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming events for the next N days.

        Args:
            max_results: Maximum number of events
            days_ahead: Number of days to look ahead
            calendar_id: Calendar ID

        Returns:
            List of upcoming events
        """
        try:
            now = datetime.now(self.timezone)
            end_date = now + timedelta(days=days_ahead)

            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now.isoformat(),
                    timeMax=end_date.isoformat(),
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            logger.info(f"Retrieved {len(events)} upcoming events")
            return [self._format_event(e) for e in events]

        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            raise

    def _format_event(self, event: Dict) -> Dict[str, Any]:
        """Format a calendar event for response."""
        start = event.get("start", {})
        end = event.get("end", {})

        # Handle all-day events vs timed events
        start_time = start.get("dateTime", start.get("date"))
        end_time = end.get("dateTime", end.get("date"))
        is_all_day = "date" in start and "dateTime" not in start

        return {
            "id": event["id"],
            "summary": event.get("summary", "(No title)"),
            "description": event.get("description"),
            "location": event.get("location"),
            "start": start_time,
            "end": end_time,
            "is_all_day": is_all_day,
            "attendees": [
                {
                    "email": a.get("email"),
                    "name": a.get("displayName"),
                    "response": a.get("responseStatus"),
                }
                for a in event.get("attendees", [])
            ],
            "organizer": event.get("organizer", {}).get("email"),
            "status": event.get("status"),
            "html_link": event.get("htmlLink"),
            "hangout_link": event.get("hangoutLink"),
            "conference_data": event.get("conferenceData"),
        }

    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """
        Create a new calendar event.

        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            attendees: List of attendee emails
            calendar_id: Calendar ID

        Returns:
            Created event info
        """
        try:
            event_body = {
                "summary": summary,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": str(self.timezone),
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": str(self.timezone),
                },
            }

            if description:
                event_body["description"] = description
            if location:
                event_body["location"] = location
            if attendees:
                event_body["attendees"] = [{"email": email} for email in attendees]

            event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )

            logger.info(f"Created event: {summary}")
            return self._format_event(event)

        except HttpError as e:
            logger.error(f"Error creating event: {e}")
            raise

    async def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any],
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """
        Update an existing event.

        Args:
            event_id: Event ID to update
            updates: Dictionary of fields to update
            calendar_id: Calendar ID

        Returns:
            Updated event info
        """
        try:
            # Get existing event
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )

            # Apply updates
            for key, value in updates.items():
                if key in ["start", "end"] and isinstance(value, datetime):
                    event[key] = {
                        "dateTime": value.isoformat(),
                        "timeZone": str(self.timezone),
                    }
                else:
                    event[key] = value

            updated_event = (
                self.service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )

            logger.info(f"Updated event: {event_id}")
            return self._format_event(updated_event)

        except HttpError as e:
            logger.error(f"Error updating event: {e}")
            raise

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> bool:
        """
        Delete a calendar event.

        Args:
            event_id: Event ID to delete
            calendar_id: Calendar ID

        Returns:
            True if successful
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
            logger.info(f"Deleted event: {event_id}")
            return True
        except HttpError as e:
            logger.error(f"Error deleting event: {e}")
            return False

    async def get_free_busy(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get free/busy information for calendars.

        Args:
            start_time: Start of range
            end_time: End of range
            calendar_ids: List of calendar IDs to check

        Returns:
            Free/busy information
        """
        try:
            calendars = calendar_ids or ["primary"]

            body = {
                "timeMin": start_time.isoformat(),
                "timeMax": end_time.isoformat(),
                "items": [{"id": cal_id} for cal_id in calendars],
            }

            result = self.service.freebusy().query(body=body).execute()

            return result.get("calendars", {})

        except HttpError as e:
            logger.error(f"Error getting free/busy: {e}")
            raise

    async def list_calendars(self) -> List[Dict[str, Any]]:
        """List all available calendars."""
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get("items", [])

            return [
                {
                    "id": cal["id"],
                    "summary": cal.get("summary"),
                    "description": cal.get("description"),
                    "primary": cal.get("primary", False),
                    "access_role": cal.get("accessRole"),
                    "background_color": cal.get("backgroundColor"),
                }
                for cal in calendars
            ]

        except HttpError as e:
            logger.error(f"Error listing calendars: {e}")
            return []
