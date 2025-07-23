from django.urls import path
from .views import project_tasks, completed_task_count

urlpatterns = [
    path('tasks/', project_tasks, name='project_tasks'),
    path('completed-count/', completed_task_count, name='completed_task_count'),
]