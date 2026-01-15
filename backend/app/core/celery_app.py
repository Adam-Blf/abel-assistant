"""
A.B.E.L - Celery Configuration for Background Tasks
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "abel",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.modules.social.tasks",
        "app.modules.productivity.tasks",
        "app.modules.api_explorer.tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Paris",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
)

# Scheduled tasks (Beat)
celery_app.conf.beat_schedule = {
    # Analyse des tendances Twitter toutes les 6 heures
    "analyze-twitter-trends": {
        "task": "app.modules.social.tasks.analyze_trends",
        "schedule": crontab(hour="*/6", minute=0),
    },
    # Vérification des emails toutes les 15 minutes
    "check-emails": {
        "task": "app.modules.productivity.tasks.check_new_emails",
        "schedule": crontab(minute="*/15"),
    },
    # Rappel des événements du calendrier toutes les heures
    "check-calendar": {
        "task": "app.modules.productivity.tasks.check_upcoming_events",
        "schedule": crontab(minute=0),
    },
    # Découverte d'APIs publiques quotidienne
    "discover-apis": {
        "task": "app.modules.api_explorer.tasks.discover_new_apis",
        "schedule": crontab(hour=3, minute=0),
    },
}
