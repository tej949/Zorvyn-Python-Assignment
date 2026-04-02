"""Tests for Analytics app"""
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import date
from decimal import Decimal

from apps.users.models import User
from apps.transactions.models import Transaction
from apps.analytics.services import AnalyticsService


class AnalyticsServiceTestCase(TestCase):
    """Test cases for AnalyticsService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123',
            role='analyst'
        )
        
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('5000.00'),
            type='income',
            category='salary',
            date=date.today(),
            description='Monthly salary'
        )
        
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            type='expense',
            category='food',
            date=date.today(),
            description='Grocery'
        )
        
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            type='expense',
            category='transport',
            date=date.today(),
            description='Taxi'
        )
        
        self.service = AnalyticsService(self.user)
    
    def test_get_summary(self):
        """Test getting financial summary"""
        summary = self.service.get_summary()
        
        self.assertEqual(summary['total_income'], 5000.0)
        self.assertEqual(summary['total_expenses'], 150.0)
        self.assertEqual(summary['current_balance'], 4850.0)
        self.assertEqual(summary['transaction_count'], 3)
    
    def test_get_category_breakdown(self):
        """Test getting category breakdown"""
        breakdown = self.service.get_category_breakdown()
        
        self.assertIn('income_by_category', breakdown)
        self.assertIn('expense_by_category', breakdown)
        self.assertEqual(breakdown['income_by_category']['salary'], 5000.0)
        self.assertEqual(breakdown['expense_by_category']['food'], 100.0)
        self.assertEqual(breakdown['expense_by_category']['transport'], 50.0)
    
    def test_get_recent_activity(self):
        """Test getting recent activity"""
        recent = self.service.get_recent_activity(limit=5)
        
        self.assertIn('recent_transactions', recent)
        self.assertEqual(len(recent['recent_transactions']), 3)
    
    def test_get_category_totals(self):
        """Test getting category totals"""
        totals = self.service.get_category_totals()
        
        self.assertIn('salary', totals)
        self.assertIn('food', totals)
        self.assertIn('transport', totals)
    
    def test_get_category_totals_by_type(self):
        """Test getting category totals by type"""
        income_totals = self.service.get_category_totals(transaction_type='income')
        expense_totals = self.service.get_category_totals(transaction_type='expense')
        
        self.assertIn('salary', income_totals)
        self.assertNotIn('salary', expense_totals)
        self.assertIn('food', expense_totals)


class AnalyticsAPITestCase(APITestCase):
    """Test cases for Analytics API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123',
            role='analyst'
        )
        
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('5000.00'),
            type='income',
            category='salary',
            date=date.today(),
            description='Monthly salary'
        )
        
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            type='expense',
            category='food',
            date=date.today(),
            description='Grocery'
        )
        
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            type='expense',
            category='transport',
            date=date.today(),
            description='Taxi'
        )
        
        self.client.force_authenticate(user=self.user)
        self.analytics_url = reverse('analytics-summary')
    
    def test_get_summary(self):
        """Test getting summary"""
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertEqual(response.data['data']['total_income'], 5000.0)
        self.assertEqual(response.data['data']['total_expenses'], 150.0)
    
    def test_get_category_breakdown(self):
        """Test getting category breakdown"""
        url = reverse('analytics-category_breakdown')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertIn('income_by_category', response.data['data'])
        self.assertIn('expense_by_category', response.data['data'])
    
    def test_get_monthly_totals(self):
        """Test getting monthly totals"""
        url = reverse('analytics-monthly_totals')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertIn('months', response.data['data'])
    
    def test_get_recent_activity(self):
        """Test getting recent activity"""
        url = reverse('analytics-recent_activity')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertIn('recent_transactions', response.data['data'])
    
    def test_get_spending_trend(self):
        """Test getting spending trend"""
        url = reverse('analytics-spending_trend')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertIn('trend', response.data['data'])
    
    def test_export_csv(self):
        """Test exporting analytics to CSV"""
        url = reverse('analytics-export_csv')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
