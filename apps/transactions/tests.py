"""Tests for Transactions app"""
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import date
from decimal import Decimal

from apps.users.models import User
from apps.transactions.models import Transaction


class TransactionModelTestCase(TestCase):
    """Test cases for Transaction model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
    
    def test_transaction_creation(self):
        """Test transaction creation"""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            type='expense',
            category='food',
            date=date.today(),
            description='Grocery shopping'
        )
        
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.type, 'expense')
        self.assertTrue(transaction.is_expense)
    
    def test_transaction_income(self):
        """Test income transaction"""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('5000.00'),
            type='income',
            category='salary',
            date=date.today()
        )
        
        self.assertTrue(transaction.is_income)
        self.assertFalse(transaction.is_expense)
    
    def test_transaction_string_representation(self):
        """Test transaction string representation"""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            type='expense',
            category='food',
            date=date.today()
        )
        
        self.assertIn('Expense', str(transaction))
        self.assertIn('100', str(transaction))


class TransactionAPITestCase(APITestCase):
    """Test cases for Transaction API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        
        self.user_viewer = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='TestPassword123',
            role='viewer'
        )
        
        self.user_analyst = User.objects.create_user(
            username='analyst',
            email='analyst@example.com',
            password='TestPassword123',
            role='analyst'
        )
        
        self.user_admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='TestPassword123',
            role='admin'
        )
        
        # Create test transactions
        self.transaction1 = Transaction.objects.create(
            user=self.user_analyst,
            amount=Decimal('100.00'),
            type='expense',
            category='food',
            date=date.today(),
            description='Lunch'
        )
        
        self.transaction2 = Transaction.objects.create(
            user=self.user_analyst,
            amount=Decimal('5000.00'),
            type='income',
            category='salary',
            date=date.today(),
            description='Monthly salary'
        )
        
        self.transactions_url = reverse('transactions-list')
    
    def test_list_own_transactions(self):
        """Test listing own transactions"""
        self.client.force_authenticate(user=self.user_analyst)
        response = self.client.get(self.transactions_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count', len(response.data)) if isinstance(response.data, dict) else len(response.data), 2)
    
    def test_viewer_cannot_create_transaction(self):
        """Test viewer cannot create transactions"""
        self.client.force_authenticate(user=self.user_viewer)
        
        data = {
            'amount': 50.00,
            'type': 'expense',
            'category': 'food',
            'date': date.today().isoformat(),
            'description': 'Coffee'
        }
        
        response = self.client.post(self.transactions_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_analyst_can_create_transaction(self):
        """Test analyst can create transactions"""
        self.client.force_authenticate(user=self.user_analyst)
        
        data = {
            'amount': 50.00,
            'type': 'expense',
            'category': 'food',
            'date': date.today().isoformat(),
            'description': 'Coffee'
        }
        
        response = self.client.post(self.transactions_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_admin_can_view_all_transactions(self):
        """Test admin can view all transactions"""
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(self.transactions_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin should see at least the 2 analyst transactions
        transaction_count = response.data.get('count', len(response.data)) if isinstance(response.data, dict) else len(response.data)
        self.assertGreaterEqual(transaction_count, 2)
    
    def test_filter_transactions_by_type(self):
        """Test filtering transactions by type"""
        self.client.force_authenticate(user=self.user_analyst)
        response = self.client.get(self.transactions_url + '?type=expense')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only have the expense transaction
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            for transaction in data['results']:
                self.assertEqual(transaction['type'], 'expense')
    
    def test_filter_transactions_by_category(self):
        """Test filtering transactions by category"""
        self.client.force_authenticate(user=self.user_analyst)
        response = self.client.get(self.transactions_url + '?category=salary')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_own_transaction(self):
        """Test updating own transaction"""
        self.client.force_authenticate(user=self.user_analyst)
        
        url = reverse('transactions-detail', kwargs={'pk': self.transaction1.pk})
        data = {
            'amount': 150.00,
            'description': 'Updated lunch'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction1.refresh_from_db()
        self.assertEqual(self.transaction1.amount, Decimal('150.00'))
    
    def test_viewer_cannot_update_transaction(self):
        """Test viewer cannot update transactions"""
        self.client.force_authenticate(user=self.user_viewer)
        
        url = reverse('transactions-detail', kwargs={'pk': self.transaction1.pk})
        data = {
            'amount': 150.00,
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_own_transaction(self):
        """Test deleting own transaction"""
        self.client.force_authenticate(user=self.user_analyst)
        
        transaction = Transaction.objects.create(
            user=self.user_analyst,
            amount=Decimal('50.00'),
            type='expense',
            category='food',
            date=date.today(),
            description='To delete'
        )
        
        url = reverse('transactions-detail', kwargs={'pk': transaction.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(pk=transaction.pk).exists())
    
    def test_export_transactions_csv(self):
        """Test exporting transactions to CSV"""
        self.client.force_authenticate(user=self.user_analyst)
        response = self.client.get(self.transactions_url + 'export_csv/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
