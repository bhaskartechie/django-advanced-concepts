from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsAssignedOrAdmin
import logging

logger = logging.getLogger('tasks')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('assigned_to')
    serializer_class = TaskSerializer
    permission_classes = [IsAssignedOrAdmin]
    search_fields = ['title', 'description']
    filterset_fields = ['priority', 'due_date']

    def perform_create(self, serializer):
        logger.debug(f"Creating task with data: {serializer.validated_data}")
        serializer.save(assigned_to=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAssignedOrAdmin])
    def high_priority(self, request):
        tasks = self.get_queryset().filter(priority='high')
        serializer = self.get_serializer(tasks, many=True)
        logger.debug("Fetched high-priority tasks")
        return Response(serializer.data)
