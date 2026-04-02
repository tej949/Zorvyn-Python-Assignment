"""
Permissions for Users app
"""
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is owner of the object or admin
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.is_authenticated and request.user.is_admin():
            return True
        
        # Owner can access their own object
        return obj == request.user


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if user is admin
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsAnalystOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is analyst or admin
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_analyst() or request.user.is_admin())
        )


class IsViewer(permissions.BasePermission):
    """
    Permission to check if user is viewer or higher
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['viewer', 'analyst', 'admin']
