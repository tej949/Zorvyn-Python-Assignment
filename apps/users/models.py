"""
User models for Finance System Backend
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.conf import settings


class User(AbstractUser):
    """Custom User model with role-based access control"""
    
    ROLE_CHOICES = (
        ('viewer', 'Viewer'),
        ('analyst', 'Analyst'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        help_text='User role determines access level and permissions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_user'
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_viewer(self):
        """Check if user is a viewer"""
        return self.role == 'viewer'
    
    def is_analyst(self):
        """Check if user is an analyst"""
        return self.role == 'analyst'
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
