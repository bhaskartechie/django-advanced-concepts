from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils.formats import date_format
from .models import Task
from datetime import date


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.ReadOnlyField(source='assigned_to.username')
    formatted_due_date = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'due_date',
            'formatted_due_date',
            'priority',
            'priority_display',
            'assigned_to',
        ]
        extra_kwargs = {
            'title': {'verbose_name': _("Title")},
            'description': {'verbose_name': _("Description")},
            'due_date': {'verbose_name': _("Due Date")},
            'priority': {'verbose_name': _("Priority")},
        }

    def get_formatted_due_date(self, obj):
        return date_format(obj.due_date, format='SHORT_DATE_FORMAT')

    def get_priority_display(self, obj):
        return obj.get_priority_display()

    def validate_priority(self, value):
        if value not in ['low', 'medium', 'high']:
            raise serializers.ValidationError(
                _("Priority must be 'low', 'medium', or 'high'")
            )
        return value

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError(_("Due date cannot be in the past"))
        return value
