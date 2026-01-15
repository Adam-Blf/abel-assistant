"""
A.B.E.L - Google Contacts Service
Contact management
"""

from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.logging import logger


class ContactsService:
    """
    Google Contacts (People API) integration:
    - List contacts
    - Search contacts
    - Create/update contacts
    - Contact groups
    """

    SCOPES = [
        "https://www.googleapis.com/auth/contacts",
        "https://www.googleapis.com/auth/contacts.readonly",
    ]

    def __init__(self, credentials: Credentials):
        self.service = build("people", "v1", credentials=credentials)

    # ========================================
    # CONTACT OPERATIONS
    # ========================================
    async def list_contacts(
        self,
        page_size: int = 100,
        person_fields: str = "names,emailAddresses,phoneNumbers,organizations,photos",
    ) -> List[Dict[str, Any]]:
        """List all contacts"""
        try:
            contacts = []
            page_token = None

            while True:
                results = (
                    self.service.people()
                    .connections()
                    .list(
                        resourceName="people/me",
                        pageSize=page_size,
                        personFields=person_fields,
                        pageToken=page_token,
                    )
                    .execute()
                )
                contacts.extend(results.get("connections", []))
                page_token = results.get("nextPageToken")
                if not page_token:
                    break

            return contacts
        except Exception as e:
            logger.error(f"Contacts list error: {e}")
            return []

    async def get_contact(
        self,
        resource_name: str,
        person_fields: str = "names,emailAddresses,phoneNumbers,organizations,photos,addresses,birthdays,biographies",
    ) -> Optional[Dict[str, Any]]:
        """Get a specific contact"""
        try:
            return (
                self.service.people()
                .get(resourceName=resource_name, personFields=person_fields)
                .execute()
            )
        except Exception as e:
            logger.error(f"Contacts get error: {e}")
            return None

    async def search_contacts(
        self,
        query: str,
        page_size: int = 30,
    ) -> List[Dict[str, Any]]:
        """Search contacts by name or email"""
        try:
            results = (
                self.service.people()
                .searchContacts(
                    query=query,
                    pageSize=page_size,
                    readMask="names,emailAddresses,phoneNumbers,organizations,photos",
                )
                .execute()
            )
            return [r.get("person", {}) for r in results.get("results", [])]
        except Exception as e:
            logger.error(f"Contacts search error: {e}")
            return []

    async def create_contact(
        self,
        given_name: str,
        family_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        organization: Optional[str] = None,
        job_title: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new contact"""
        try:
            person = {
                "names": [
                    {
                        "givenName": given_name,
                        "familyName": family_name or "",
                    }
                ]
            }

            if email:
                person["emailAddresses"] = [{"value": email}]
            if phone:
                person["phoneNumbers"] = [{"value": phone}]
            if organization or job_title:
                person["organizations"] = [
                    {
                        "name": organization or "",
                        "title": job_title or "",
                    }
                ]
            if notes:
                person["biographies"] = [{"value": notes}]

            return (
                self.service.people()
                .createContact(body=person)
                .execute()
            )
        except Exception as e:
            logger.error(f"Contacts create error: {e}")
            return None

    async def update_contact(
        self,
        resource_name: str,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a contact"""
        try:
            # Get current contact first
            contact = await self.get_contact(resource_name)
            if not contact:
                return None

            # Update fields
            if given_name or family_name:
                if "names" not in contact:
                    contact["names"] = [{}]
                if given_name:
                    contact["names"][0]["givenName"] = given_name
                if family_name:
                    contact["names"][0]["familyName"] = family_name

            if email:
                contact["emailAddresses"] = [{"value": email}]
            if phone:
                contact["phoneNumbers"] = [{"value": phone}]

            update_mask = "names,emailAddresses,phoneNumbers"

            return (
                self.service.people()
                .updateContact(
                    resourceName=resource_name,
                    body=contact,
                    updatePersonFields=update_mask,
                )
                .execute()
            )
        except Exception as e:
            logger.error(f"Contacts update error: {e}")
            return None

    async def delete_contact(self, resource_name: str) -> bool:
        """Delete a contact"""
        try:
            self.service.people().deleteContact(
                resourceName=resource_name
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Contacts delete error: {e}")
            return False

    # ========================================
    # CONTACT GROUPS
    # ========================================
    async def list_contact_groups(self) -> List[Dict[str, Any]]:
        """List all contact groups"""
        try:
            results = self.service.contactGroups().list().execute()
            return results.get("contactGroups", [])
        except Exception as e:
            logger.error(f"Contact groups list error: {e}")
            return []

    async def get_contact_group(
        self,
        resource_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a contact group"""
        try:
            return (
                self.service.contactGroups()
                .get(resourceName=resource_name, maxMembers=1000)
                .execute()
            )
        except Exception as e:
            logger.error(f"Contact groups get error: {e}")
            return None

    async def create_contact_group(self, name: str) -> Optional[Dict[str, Any]]:
        """Create a new contact group"""
        try:
            body = {"contactGroup": {"name": name}}
            return self.service.contactGroups().create(body=body).execute()
        except Exception as e:
            logger.error(f"Contact groups create error: {e}")
            return None

    async def delete_contact_group(
        self,
        resource_name: str,
        delete_contacts: bool = False,
    ) -> bool:
        """Delete a contact group"""
        try:
            self.service.contactGroups().delete(
                resourceName=resource_name,
                deleteContacts=delete_contacts,
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Contact groups delete error: {e}")
            return False

    async def add_to_group(
        self,
        group_resource_name: str,
        contact_resource_names: List[str],
    ) -> bool:
        """Add contacts to a group"""
        try:
            body = {"resourceNamesToAdd": contact_resource_names}
            self.service.contactGroups().members().modify(
                resourceName=group_resource_name, body=body
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Contact groups add error: {e}")
            return False

    async def remove_from_group(
        self,
        group_resource_name: str,
        contact_resource_names: List[str],
    ) -> bool:
        """Remove contacts from a group"""
        try:
            body = {"resourceNamesToRemove": contact_resource_names}
            self.service.contactGroups().members().modify(
                resourceName=group_resource_name, body=body
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Contact groups remove error: {e}")
            return False

    # ========================================
    # HELPER METHODS
    # ========================================
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find contact by email"""
        contacts = await self.search_contacts(email)
        for contact in contacts:
            emails = contact.get("emailAddresses", [])
            for e in emails:
                if e.get("value", "").lower() == email.lower():
                    return contact
        return None

    async def find_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Find contact by phone number"""
        # Normalize phone number
        normalized = "".join(c for c in phone if c.isdigit())

        contacts = await self.list_contacts()
        for contact in contacts:
            phones = contact.get("phoneNumbers", [])
            for p in phones:
                contact_phone = "".join(c for c in p.get("value", "") if c.isdigit())
                if contact_phone.endswith(normalized) or normalized.endswith(contact_phone):
                    return contact
        return None

    async def get_contact_count(self) -> int:
        """Get total number of contacts"""
        contacts = await self.list_contacts(person_fields="names")
        return len(contacts)
