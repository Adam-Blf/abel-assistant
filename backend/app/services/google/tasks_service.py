"""
A.B.E.L - Google Tasks Service
Task management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.logging import logger


class TasksService:
    """
    Google Tasks integration:
    - Task lists management
    - Task CRUD operations
    - Due dates
    - Subtasks
    """

    SCOPES = [
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/tasks.readonly",
    ]

    def __init__(self, credentials: Credentials):
        self.service = build("tasks", "v1", credentials=credentials)

    # ========================================
    # TASK LIST OPERATIONS
    # ========================================
    async def list_task_lists(self) -> List[Dict[str, Any]]:
        """Get all task lists"""
        try:
            results = self.service.tasklists().list().execute()
            return results.get("items", [])
        except Exception as e:
            logger.error(f"Tasks list task lists error: {e}")
            return []

    async def get_task_list(self, tasklist_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task list"""
        try:
            return self.service.tasklists().get(tasklist=tasklist_id).execute()
        except Exception as e:
            logger.error(f"Tasks get task list error: {e}")
            return None

    async def create_task_list(self, title: str) -> Optional[Dict[str, Any]]:
        """Create a new task list"""
        try:
            body = {"title": title}
            return self.service.tasklists().insert(body=body).execute()
        except Exception as e:
            logger.error(f"Tasks create task list error: {e}")
            return None

    async def update_task_list(
        self,
        tasklist_id: str,
        title: str,
    ) -> Optional[Dict[str, Any]]:
        """Update a task list"""
        try:
            body = {"title": title}
            return (
                self.service.tasklists()
                .update(tasklist=tasklist_id, body=body)
                .execute()
            )
        except Exception as e:
            logger.error(f"Tasks update task list error: {e}")
            return None

    async def delete_task_list(self, tasklist_id: str) -> bool:
        """Delete a task list"""
        try:
            self.service.tasklists().delete(tasklist=tasklist_id).execute()
            return True
        except Exception as e:
            logger.error(f"Tasks delete task list error: {e}")
            return False

    # ========================================
    # TASK OPERATIONS
    # ========================================
    async def list_tasks(
        self,
        tasklist_id: str = "@default",
        show_completed: bool = True,
        show_hidden: bool = False,
        due_min: Optional[str] = None,
        due_max: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List tasks in a task list"""
        try:
            params = {
                "tasklist": tasklist_id,
                "showCompleted": show_completed,
                "showHidden": show_hidden,
            }
            if due_min:
                params["dueMin"] = due_min
            if due_max:
                params["dueMax"] = due_max

            results = self.service.tasks().list(**params).execute()
            return results.get("items", [])
        except Exception as e:
            logger.error(f"Tasks list tasks error: {e}")
            return []

    async def get_task(
        self,
        tasklist_id: str,
        task_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a specific task"""
        try:
            return (
                self.service.tasks()
                .get(tasklist=tasklist_id, task=task_id)
                .execute()
            )
        except Exception as e:
            logger.error(f"Tasks get task error: {e}")
            return None

    async def create_task(
        self,
        tasklist_id: str,
        title: str,
        notes: Optional[str] = None,
        due: Optional[str] = None,  # RFC 3339 format
        parent: Optional[str] = None,  # For subtasks
    ) -> Optional[Dict[str, Any]]:
        """Create a new task"""
        try:
            body = {"title": title}
            if notes:
                body["notes"] = notes
            if due:
                body["due"] = due

            params = {"tasklist": tasklist_id, "body": body}
            if parent:
                params["parent"] = parent

            return self.service.tasks().insert(**params).execute()
        except Exception as e:
            logger.error(f"Tasks create task error: {e}")
            return None

    async def update_task(
        self,
        tasklist_id: str,
        task_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due: Optional[str] = None,
        status: Optional[str] = None,  # needsAction, completed
    ) -> Optional[Dict[str, Any]]:
        """Update a task"""
        try:
            task = await self.get_task(tasklist_id, task_id)
            if not task:
                return None

            if title:
                task["title"] = title
            if notes:
                task["notes"] = notes
            if due:
                task["due"] = due
            if status:
                task["status"] = status
                if status == "completed":
                    task["completed"] = datetime.utcnow().isoformat() + "Z"

            return (
                self.service.tasks()
                .update(tasklist=tasklist_id, task=task_id, body=task)
                .execute()
            )
        except Exception as e:
            logger.error(f"Tasks update task error: {e}")
            return None

    async def complete_task(
        self,
        tasklist_id: str,
        task_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark task as completed"""
        return await self.update_task(tasklist_id, task_id, status="completed")

    async def uncomplete_task(
        self,
        tasklist_id: str,
        task_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark task as not completed"""
        return await self.update_task(tasklist_id, task_id, status="needsAction")

    async def delete_task(self, tasklist_id: str, task_id: str) -> bool:
        """Delete a task"""
        try:
            self.service.tasks().delete(
                tasklist=tasklist_id, task=task_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Tasks delete task error: {e}")
            return False

    async def move_task(
        self,
        tasklist_id: str,
        task_id: str,
        parent: Optional[str] = None,
        previous: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Move a task (reorder or make subtask)"""
        try:
            params = {"tasklist": tasklist_id, "task": task_id}
            if parent:
                params["parent"] = parent
            if previous:
                params["previous"] = previous

            return self.service.tasks().move(**params).execute()
        except Exception as e:
            logger.error(f"Tasks move task error: {e}")
            return None

    async def clear_completed(self, tasklist_id: str) -> bool:
        """Clear all completed tasks from a list"""
        try:
            self.service.tasks().clear(tasklist=tasklist_id).execute()
            return True
        except Exception as e:
            logger.error(f"Tasks clear completed error: {e}")
            return False

    # ========================================
    # HELPER METHODS
    # ========================================
    async def get_all_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all tasks from all task lists"""
        task_lists = await self.list_task_lists()
        result = {}

        for tl in task_lists:
            tasks = await self.list_tasks(tl["id"])
            result[tl["title"]] = tasks

        return result

    async def get_due_today(self) -> List[Dict[str, Any]]:
        """Get tasks due today"""
        today = datetime.utcnow().date().isoformat() + "T00:00:00Z"
        tomorrow = datetime.utcnow().date().isoformat() + "T23:59:59Z"

        task_lists = await self.list_task_lists()
        due_today = []

        for tl in task_lists:
            tasks = await self.list_tasks(
                tl["id"], due_min=today, due_max=tomorrow
            )
            for task in tasks:
                task["tasklist_id"] = tl["id"]
                task["tasklist_title"] = tl["title"]
                due_today.append(task)

        return due_today

    async def get_overdue(self) -> List[Dict[str, Any]]:
        """Get overdue tasks"""
        now = datetime.utcnow().isoformat() + "Z"

        task_lists = await self.list_task_lists()
        overdue = []

        for tl in task_lists:
            tasks = await self.list_tasks(tl["id"], due_max=now)
            for task in tasks:
                if task.get("status") != "completed":
                    task["tasklist_id"] = tl["id"]
                    task["tasklist_title"] = tl["title"]
                    overdue.append(task)

        return overdue

    async def quick_add(self, title: str, due_days: int = 0) -> Optional[Dict[str, Any]]:
        """Quickly add a task to default list"""
        due = None
        if due_days > 0:
            from datetime import timedelta
            due_date = datetime.utcnow() + timedelta(days=due_days)
            due = due_date.isoformat() + "Z"

        return await self.create_task("@default", title, due=due)
