"""Audit service logic for Finance System"""
from apps.audit.models import AuditLog
from apps.transactions.models import Transaction


class AuditService:
    """Service class for audit logging"""
    
    @staticmethod
    def log_action(user, action, model_name, object_id=None, changes=None, ip_address=None, user_agent=None):
        """
        Log an action
        
        Args:
            user: User who performed the action
            action: Action type (create, update, delete, etc.)
            model_name: Name of the model
            object_id: ID of the object affected
            changes: Dictionary of changes {field: [old_value, new_value]}
            ip_address: IP address of the request
            user_agent: User agent string
        """
        AuditLog.objects.create(
            user=user,
            action=action,
            model=model_name,
            object_id=object_id,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    @staticmethod
    def get_user_logs(user, limit=50):
        """Get audit logs for a user"""
        return AuditLog.objects.filter(user=user).order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_model_logs(model_name, limit=50):
        """Get audit logs for a model"""
        return AuditLog.objects.filter(model=model_name).order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_action_logs(action, limit=50):
        """Get audit logs for an action"""
        return AuditLog.objects.filter(action=action).order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_object_logs(model_name, object_id):
        """Get audit logs for a specific object"""
        return AuditLog.objects.filter(
            model=model_name,
            object_id=object_id
        ).order_by('-timestamp')
