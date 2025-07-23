from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name
# Database optimization: Index on name for faster lookups
    class Meta:
        indexes = [
            models.Index(fields=['name']),  # Index for faster lookups
        ]


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
# Database optimization: Index on project and status for faster queries
    class Meta:
        indexes = [
            models.Index(fields=['project', 'status']),  # Index for common queries
        ]
