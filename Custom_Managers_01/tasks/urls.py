from django.urls import path
from tasks.views import pending_tasks, high_priority_tasks, recent_pending_tasks

urlpatterns = [
    path('pending/', pending_tasks, name='pending_tasks'),
    path('high-priority/', high_priority_tasks, name='high_priority_tasks'),
    path('recent/', recent_pending_tasks, name='recent_pending_tasks'),
]
