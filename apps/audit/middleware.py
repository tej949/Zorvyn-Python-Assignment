"""Middleware for audit logging"""
from apps.audit.services import AuditService
import json


class AuditLoggingMiddleware:
    """Middleware for logging API actions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get IP address
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Process the request
        response = self.get_response(request)
        
        # Log the action if it's an API endpoint and user is authenticated
        if request.path.startswith('/api/') and request.user.is_authenticated:
            self.log_api_action(request, response, ip_address, user_agent)
        
        return response
    
    def log_api_action(self, request, response, ip_address, user_agent):
        """Log API action"""
        method = request.method
        path = request.path
        
        # Determine action type
        if method == 'POST':
            action = 'create'
        elif method in ['PUT', 'PATCH']:
            action = 'update'
        elif method == 'DELETE':
            action = 'delete'
        elif method == 'GET':
            action = 'retrieve'
        else:
            return
        
        # Determine model name
        model_name = self.get_model_from_path(path)
        
        if not model_name:
            return
        
        # Get object ID if it's a detail endpoint
        object_id = self.get_object_id_from_path(path)
        
        # Get changes from request body
        changes = {}
        if method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'data'):
            try:
                changes = dict(request.data)
            except:
                pass
        
        # Log the action
        AuditService.log_action(
            user=request.user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_model_from_path(path):
        """Extract model name from API path"""
        parts = path.strip('/').split('/')
        
        # Pattern: /api/transactions/123/
        if len(parts) >= 2:
            if parts[1] in ['transactions', 'users', 'analytics', 'audit-logs']:
                return parts[1].replace('-logs', 'Log').replace('-', '_').title()
        
        return None
    
    @staticmethod
    def get_object_id_from_path(path):
        """Extract object ID from API path"""
        parts = path.strip('/').split('/')
        
        # Pattern: /api/transactions/123/
        if len(parts) >= 3:
            try:
                return int(parts[2])
            except (ValueError, IndexError):
                return None
        
        return None
