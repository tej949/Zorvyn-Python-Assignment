"""Serializers for Audit app"""
from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'username',
            'action',
            'action_display',
            'model',
            'object_id',
            'changes',
            'ip_address',
            'user_agent',
            'timestamp',
        ]
        read_only_fields = fields
