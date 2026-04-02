"""Tests for Audit app"""
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse

from apps.users.models import User
from apps.audit.models import AuditLog
from apps.audit.services import AuditService


class AuditServiceTestCase(TestCase):
    """Test cases for AuditService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
    
    def test_log_action(self):
        """Test logging an action"""
        AuditService.log_action(
            user=self.user,
            action='create',
            model_name='Transaction',
            object_id=1,
            changes={'amount': [None, 100.00]},
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0'
        )
        
        self.assertEqual(AuditLog.objects.count(), 1)
        log = AuditLog.objects.first()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'create')
        self.assertEqual(log.model, 'Transaction')
    
    def test_get_user_logs(self):
        """Test getting user logs"""
        for i in range(5):
            AuditService.log_action(
                user=self.user,
                action='create',
                model_name='Transaction',
                object_id=i,
            )
        
        logs = AuditService.get_user_logs(self.user)
        self.assertEqual(len(logs), 5)
    
    def test_get_action_logs(self):
        """Test getting action logs"""
        for i in range(3):
            AuditService.log_action(
                user=self.user,
                action='create',
                model_name='Transaction',
                object_id=i,
            )
        
        for i in range(2):
            AuditService.log_action(
                user=self.user,
                action='update',
                model_name='Transaction',
                object_id=i,
            )
        
        create_logs = AuditService.get_action_logs('create')
        update_logs = AuditService.get_action_logs('update')
        
        self.assertEqual(len(create_logs), 3)
        self.assertEqual(len(update_logs), 2)


class AuditLogAPITestCase(APITestCase):
    """Test cases for Audit Log API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        
        self.user_admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='TestPassword123',
            role='admin'
        )
        
        self.user_analyst = User.objects.create_user(
            username='analyst',
            email='analyst@example.com',
            password='TestPassword123',
            role='analyst'
        )
        
        # Create audit logs
        for i in range(5):
            AuditService.log_action(
                user=self.user_admin,
                action='create',
                model_name='Transaction',
                object_id=i,
            )
        
        self.audit_url = reverse('audit-logs-list')
    
    def test_admin_can_view_audit_logs(self):
        """Test admin can view audit logs"""
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(self.audit_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_analyst_cannot_view_all_audit_logs(self):
        """Test analyst cannot view all audit logs"""
        self.client.force_authenticate(user=self.user_analyst)
        response = self.client.get(self.audit_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_filter_by_user(self):
        """Test filtering audit logs by user"""
        self.client.force_authenticate(user=self.user_admin)
        url = reverse('audit-logs-by_user')
        response = self.client.get(url + f'?user_id={self.user_admin.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_by_action(self):
        """Test filtering audit logs by action"""
        self.client.force_authenticate(user=self.user_admin)
        url = reverse('audit-logs-by_action')
        response = self.client.get(url + '?action=create')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_export_csv(self):
        """Test exporting audit logs to CSV"""
        self.client.force_authenticate(user=self.user_admin)
        url = reverse('audit-logs-export_csv')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
