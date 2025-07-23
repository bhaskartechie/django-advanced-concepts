from django.http import HttpResponse
from .models import Project, Task
from django.db.models import Count

# def project_tasks(request):
#     projects = Project.objects.all()
#     result = []
#     for project in projects:
#         # N+1 query problem: Fetch tasks for each project separately
#         tasks = project.tasks.all()
#         task_titles = [task.title for task in tasks]
#         result.append(f"Project: {project.name}, Tasks: {', '.join(task_titles)}")
#     return HttpResponse("<br>".join(result))


# def completed_task_count(request):
#     projects = Project.objects.all()
#     result = []
#     for project in projects:
#         # Inefficient: Fetch all tasks and count completed ones in Python
#         completed_count = sum(
#             1 for task in project.tasks.all() if task.status == 'completed'
#         )
#         result.append(f"Project: {project.name}, Completed Tasks: {completed_count}")
#     return HttpResponse("<br>".join(result))


def project_tasks(request):
    # Use prefetch_related to fetch tasks in one query
    projects = Project.objects.prefetch_related('tasks').all()
    result = []
    for project in projects:
        # Tasks are already fetched, no additional queries
        task_titles = [task.title for task in project.tasks.all()]  # No extra query
        result.append(f"Project: {project.name}, Tasks: {', '.join(task_titles)}")
    return HttpResponse("<br>".join(result))

def completed_task_count(request):
    # Use annotate to count completed tasks at the database level
    projects = Project.objects.annotate(
        completed_count=Count('tasks', filter=models.Q(tasks__status='completed'))
    )
    result = [f"Project: {project.name}, Completed Tasks: {project.completed_count}" for project in projects]
    return HttpResponse("<br>".join(result))