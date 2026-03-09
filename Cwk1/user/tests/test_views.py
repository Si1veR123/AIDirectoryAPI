from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tool.models import Domain, Developer, Accessibility, ContextWindow, Tool


class RegisterViewTest(TestCase):
    """Test cases for RegisterView"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

    def test_register_user(self):
        """Test registering a new user"""
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com'
        }
        response = self.client.post('/api/user/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created
        User = get_user_model()
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_user_with_weak_password(self):
        """Test registering with weak password fails"""
        data = {
            'username': 'newuser',
            'password': '123',
            'email': 'new@example.com'
        }
        response = self.client.post('/api/user/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Test registering with duplicate username fails"""
        User = get_user_model()
        User.objects.create_user(
            username='existing',
            password='pass123'
        )
        
        data = {
            'username': 'existing',
            'password': 'newpass123'
        }
        response = self.client.post('/api/user/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_additional_fields(self):
        """Test registering with additional profile fields"""
        domain = Domain.objects.create(name="Testing")
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com',
            'email_alerts': True,
            'interested_domain': domain.name,
            'bio': 'Test bio'
        }
        response = self.client.post('/api/user/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CurrentUserDetailViewTest(TestCase):
    """Test cases for CurrentUserDetailView"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def test_get_current_user_authenticated(self):
        """Test retrieving current user profile when authenticated"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/user/current/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_current_user_unauthenticated(self):
        """Test retrieving current user when not authenticated fails"""
        response = self.client.get('/api/user/current/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_current_user(self):
        """Test updating current user profile"""
        self.client.force_authenticate(user=self.user)
        data = {
            'username': 'testuser',
            'email': 'updated@example.com',
            'bio': 'Updated bio'
        }
        response = self.client.patch('/api/user/current/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.bio, 'Updated bio')

    def test_update_password(self):
        """Test updating user password"""
        self.client.force_authenticate(user=self.user)
        data = {
            'username': 'testuser',
            'password': 'newpassword123'
        }
        response = self.client.patch('/api/user/current/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_delete_current_user(self):
        """Test deleting current user account"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete('/api/user/current/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        User = get_user_model()
        self.assertFalse(User.objects.filter(username='testuser').exists())


class UserViewSetTest(TestCase):
    """Test cases for UserViewSet (admin endpoints)"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )

    def test_list_users_as_admin(self):
        """Test listing all users as admin"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_users_as_regular_user(self):
        """Test that regular users cannot list all users"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_as_admin(self):
        """Test retrieving a specific user as admin"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/user/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_create_user_as_admin(self):
        """Test creating a user as admin"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'newuser',
            'password': 'StrongPassword123!',
            'email': 'new@example.com'
        }
        response = self.client.post('/api/user/', data)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_user_as_admin(self):
        """Test updating a user as admin"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'testuser',
            'email': 'updated@example.com'
        }
        response = self.client.patch(f'/api/user/{self.user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_as_admin(self):
        """Test deleting a user as admin"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/user/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CurrentUserFavouriteToolViewSetTest(TestCase):
    """Test cases for CurrentUserFavouriteToolViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Create tool
        developer = Developer.objects.create(name="TestDev")
        domain = Domain.objects.create(name="Testing")
        accessibility = Accessibility.objects.create(name="API")
        context_window = ContextWindow.objects.create(name="32K")
        
        self.tool = Tool.objects.create(
            ai_name="TestAI",
            developer=developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=context_window,
            accessibility=accessibility,
            website_url="https://test.com"
        )

    def test_list_favourite_tools(self):
        """Test listing favourite tools"""
        self.client.force_authenticate(user=self.user)
        self.user.favourite_tools.add(self.tool)
        
        response = self.client.get('/api/user/current/favourites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ai_name'], 'TestAI')

    def test_add_favourite_tool(self):
        """Test adding a favourite tool"""
        self.client.force_authenticate(user=self.user)
        data = {'ai_name': 'TestAI'}
        response = self.client.post('/api/user/current/favourites/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertTrue(self.user.favourite_tools.filter(ai_name='TestAI').exists())

    def test_add_nonexistent_tool_as_favourite(self):
        """Test adding non-existent tool fails"""
        self.client.force_authenticate(user=self.user)
        data = {'ai_name': 'NonExistentAI'}
        response = self.client.post('/api/user/current/favourites/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_favourite_tool(self):
        """Test removing a favourite tool"""
        self.client.force_authenticate(user=self.user)
        self.user.favourite_tools.add(self.tool)
        
        response = self.client.delete(f'/api/user/current/favourites/{self.tool.ai_name}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertFalse(self.user.favourite_tools.filter(ai_name='TestAI').exists())

    def test_favourite_tools_requires_authentication(self):
        """Test that favourite tools endpoints require authentication"""
        response = self.client.get('/api/user/current/favourites/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserFavouriteToolViewSetTest(TestCase):
    """Test cases for UserFavouriteToolViewSet (admin endpoints)"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )
        
        # Create tool
        developer = Developer.objects.create(name="TestDev")
        domain = Domain.objects.create(name="Testing")
        accessibility = Accessibility.objects.create(name="API")
        context_window = ContextWindow.objects.create(name="32K")
        
        self.tool = Tool.objects.create(
            ai_name="TestAI",
            developer=developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=context_window,
            accessibility=accessibility,
            website_url="https://test.com"
        )

    def test_admin_list_user_favourites(self):
        """Test admin can list any user's favourites"""
        self.client.force_authenticate(user=self.admin)
        self.user.favourite_tools.add(self.tool)
        
        response = self.client.get(f'/api/user/{self.user.id}/favourites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_add_favourite_for_user(self):
        """Test admin can add favourite for any user"""
        self.client.force_authenticate(user=self.admin)
        data = {'ai_name': 'TestAI'}
        response = self.client.post(f'/api/user/{self.user.id}/favourites/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertTrue(self.user.favourite_tools.filter(ai_name='TestAI').exists())

    def test_admin_remove_favourite_for_user(self):
        """Test admin can remove favourite for any user"""
        self.client.force_authenticate(user=self.admin)
        self.user.favourite_tools.add(self.tool)
        
        response = self.client.delete(
            f'/api/user/{self.user.id}/favourites/{self.tool.ai_name}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_access_others_favourites(self):
        """Test regular users cannot access other users' favourites"""
        User = get_user_model()
        other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass123"
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/user/{other_user.id}/favourites/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_endpoint_requires_admin(self):
        """Test that user favourite admin endpoints require staff permission"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/user/{self.user.id}/favourites/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
