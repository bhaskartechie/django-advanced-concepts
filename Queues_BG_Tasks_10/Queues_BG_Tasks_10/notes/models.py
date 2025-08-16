from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()

# New model to track report generation status
class ReportStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_ready = models.BooleanField(default=False)
    filename = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Report status for {self.user.username}"