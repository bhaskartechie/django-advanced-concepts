from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
    ]
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    due_date = models.DateField(verbose_name=_("Due Date"))
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, verbose_name=_("Priority")
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name=_("Assigned To")
    )

    def __str__(self):
        return self.title
