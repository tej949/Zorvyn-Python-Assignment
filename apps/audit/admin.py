"""Admin configuration for Audit app"""
from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for AuditLog model"""
    
    list_display = ['id', 'user', 'action', 'model', 'object_id', 'timestamp']
    list_filter = ['action', 'model', 'timestamp']
    search_fields = ['user__username', 'model']
    readonly_fields = ['user', 'action', 'model', 'object_id', 'changes', 'ip_address', 'user_agent', 'timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """Disable adding audit logs manually"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only allow superuser to delete"""
        return request.user.is_superuser
