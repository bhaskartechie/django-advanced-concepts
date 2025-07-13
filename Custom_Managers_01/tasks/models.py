# tasks/models.py
from django.db import models
from datetime import timedelta
from django.utils import timezone


class PendingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='pending')


class TaskQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='pending')

    def high_priority(self):
        return self.filter(priority='high')

    def recent(self, days=7):
        return self.filter(
            created_at__gte=timezone.now() - timedelta(days=days)
        )

    def by_priority(self, priority):
        return self.filter(priority=priority)


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('archived', 'Archived'),
        ],
        default='pending',
    )
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='low',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()  # Default manager
    pending = PendingManager()  # Custom manager for pending tasks
    custom_objects = TaskQuerySet.as_manager()  # Custom queryset manager

    def __str__(self):
        return self.title
