"""Tests for Users app"""
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from apps.users.models import User


class UserModelTestCase(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user_viewer = User.objects.create_user(
            username='viewer_user',
            email='viewer@example.com',
            password='TestPassword123',
            role='viewer'
        )
        self.user_analyst = User.objects.create_user(
            username='analyst_user',
            email='analyst@example.com',
            password='TestPassword123',
            role='analyst'
        )
        self.user_admin = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='TestPassword123',
            role='admin'
        )
    
    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(self.user_viewer.username, 'viewer_user')
    
    def test_user_role_methods(self):
        """Test user role checking methods"""
        self.assertTrue(self.user_viewer.is_viewer())
        self.assertFalse(self.user_viewer.is_analyst())
        self.assertFalse(self.user_viewer.is_admin())
        
        self.assertTrue(self.user_analyst.is_analyst())
        self.assertTrue(self.user_admin.is_admin())
    
    def test_user_has_role(self):
        """Test has_role method"""
        self.assertTrue(self.user_viewer.has_role('viewer'))
        self.assertTrue(self.user_analyst.has_role('analyst'))
        self.assertTrue(self.user_admin.has_role('admin'))
    
    def test_user_string_representation(self):
        """Test user string representation"""
        expected = 'viewer_user (Viewer)'
        self.assertEqual(str(self.user_viewer), expected)


class UserAuthenticationTestCase(APITestCase):
    """Test cases for user authentication"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
    
    def test_user_registration(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPassword123',
            'password_confirm': 'TestPassword123',
            'role': 'viewer'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['error'])
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPassword123',
            'password_confirm': 'DifferentPassword123',
            'role': 'viewer'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'])
    
    def test_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='TestPassword123'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'TestPassword123',
            'password_confirm': 'TestPassword123',
            'role': 'viewer'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'])
    
    def test_user_login(self):
        """Test user login"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        
        data = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertIn('tokens', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(response.data['error'])


class UserProfileTestCase(APITestCase):
    """Test cases for user profile"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('self-profile')
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertEqual(response.data['data']['username'], 'testuser')
        self.assertEqual(response.data['data']['email'], 'test@example.com')
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        data = {
            'email': 'newemail@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        update_url = reverse('self-update_profile')
        response = self.client.patch(update_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
