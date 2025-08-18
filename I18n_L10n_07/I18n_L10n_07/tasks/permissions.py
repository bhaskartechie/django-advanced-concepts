from rest_framework import permissions


class IsAssignedOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow:
    - Any authenticated user to view tasks (GET, HEAD, OPTIONS).
    - Only staff or the assigned user to create, update, or delete tasks.
    """

    def has_permission(self, request, view):
        # Require authentication for all actions
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Allow POST, PUT, DELETE only for staff or the task's assigned user
        return request.user.is_staff or obj.assigned_to == request.user
