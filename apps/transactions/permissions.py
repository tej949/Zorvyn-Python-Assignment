"""Permissions for Transactions app"""
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is owner of the transaction or admin
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any transaction
        if request.user.is_authenticated and request.user.is_admin():
            return True
        
        # Owner can access their own transactions
        return obj.user == request.user


class IsAnalystOrAdmin(permissions.BasePermission):
    """
    Permission to allow analyst and admin users
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_analyst() or request.user.is_admin())
        )


class CanExportTransactions(permissions.BasePermission):
    """
    Permission to export transactions (analyst or admin)
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_analyst() or request.user.is_admin())
        )


class CanCreateTransaction(permissions.BasePermission):
    """
    Permission to create transactions (admin or own transactions)
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin can create for any user
        if request.user.is_admin():
            return True
        
        # Only analyst and admin can create, not viewer
        return request.user.is_analyst() or request.user.is_admin()
