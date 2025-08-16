import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Queues_BG_Tasks_10.settings")

app = Celery("Queues_BG_Tasks_10")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
