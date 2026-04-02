"""Audit logging models for Finance System Backend"""
from django.db import models
from django.conf import settings
import json


class AuditLog(models.Model):
    """Model for audit logging"""
    
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('retrieve', 'Retrieve'),
        ('list', 'List'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='Action performed'
    )
    
    model = models.CharField(
        max_length=100,
        help_text='Model name where action was performed'
    )
    
    object_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID of the object affected'
    )
    
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text='Field changes (field: [old_value, new_value])'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the request'
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text='User agent string'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_auditlog'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['model', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model} - {self.timestamp}"
