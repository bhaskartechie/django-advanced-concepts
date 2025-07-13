# tasks/views.py
from django.http import HttpResponse
from .models import Task


def pending_tasks(request):
    tasks = Task.pending.all()  # Clean and reusable
    return HttpResponse("<br>".join([task.title for task in tasks]))


def high_priority_tasks(request):
    tasks = Task.custom_objects.pending().high_priority()  # Chained queries
    return HttpResponse("<br>".join([task.title for task in tasks]))


def recent_pending_tasks(request):
    tasks = Task.custom_objects.pending().recent(days=7)  # Flexible and DRY
    return HttpResponse("<br>".join([task.title for task in tasks]))
