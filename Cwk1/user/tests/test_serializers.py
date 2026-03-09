from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from user.serializers import SecureUserSerializer, StandardUserSerializer
from user.models import CustomUser
from tool.models import Domain, Developer, Accessibility, ContextWindow, Tool


class StandardUserSerializerTest(TestCase):
    """Test cases for StandardUserSerializer"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def test_serialize_user(self):
        """Test serializing a user"""
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = StandardUserSerializer(
            self.user,
            context={'request': request}
        )
        
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        # Password should not be in serialized data
        self.assertNotIn('password', serializer.data)

    def test_deserialize_user_creation(self):
        """Test deserializing data to create a user"""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com'
        }
        
        serializer = StandardUserSerializer(
            data=data,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpass123'))

    def test_password_validation(self):
        """Test that weak passwords are rejected"""
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            'username': 'newuser',
            'password': '123',
            'email': 'new@example.com'
        }
        
        serializer = StandardUserSerializer(
            data=data,
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())

    def test_update_user_password(self):
        """Test updating user password"""
        request = self.factory.patch('/')
        request.user = self.user
        
        data = {'password': 'newpassword123'}
        
        serializer = StandardUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        
        self.assertTrue(user.check_password('newpassword123'))

    def test_standard_user_fields_only(self):
        """Test that StandardUserSerializer only includes user fields"""
        fields = set(StandardUserSerializer.Meta.fields)
        expected_fields = {
            'username', 'first_name', 'last_name', 'password', 'email',
            'email_alerts', 'interested_domain', 'date_of_birth',
            'bio', 'favourite_tools'
        }
        self.assertEqual(fields, expected_fields)


class SecureUserSerializerTest(TestCase):
    """Test cases for SecureUserSerializer"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.staff = User.objects.create_user(
            username="staff",
            password="staff123",
            is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="admin123"
        )

    def test_normal_user_can_modify_own_account(self):
        """Test that normal users can modify their own account"""
        request = self.factory.patch('/')
        request.user = self.user
        
        data = {'email': 'updated@example.com'}
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_normal_user_cannot_modify_other_account(self):
        """Test that normal users cannot modify other users' accounts"""
        User = get_user_model()
        other_user = User.objects.create_user(
            username="other",
            password="other123"
        )
        
        request = self.factory.patch('/')
        request.user = self.user
        
        data = {'email': 'hacked@example.com'}
        
        serializer = SecureUserSerializer(
            other_user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())

    def test_normal_user_cannot_set_staff_fields(self):
        """Test that normal users cannot set staff-only fields"""
        request = self.factory.patch('/')
        request.user = self.user
        
        data = {'is_staff': True}
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())

    def test_staff_can_modify_other_users(self):
        """Test that staff can modify other users"""
        request = self.factory.patch('/')
        request.user = self.staff
        
        data = {'email': 'updated@example.com'}
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_staff_cannot_set_superuser_fields(self):
        """Test that staff cannot set superuser-only fields"""
        request = self.factory.patch('/')
        request.user = self.staff
        
        data = {'is_superuser': True}
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertFalse(serializer.is_valid())

    def test_superuser_can_set_all_fields(self):
        """Test that superuser can set all fields"""
        request = self.factory.patch('/')
        request.user = self.superuser
        
        data = {
            'is_staff': True,
            'is_superuser': True
        }
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_user_with_interested_domain(self):
        """Test serializing user with interested domain"""
        domain = Domain.objects.create(name="Testing")
        self.user.interested_domain = domain
        self.user.save()
        
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = SecureUserSerializer(
            self.user,
            context={'request': request}
        )
        
        self.assertEqual(serializer.data['interested_domain'], domain.name)

    def test_user_with_favourite_tools(self):
        """Test serializing user with favourite tools"""
        developer = Developer.objects.create(name="TestDev")
        domain = Domain.objects.create(name="Testing")
        accessibility = Accessibility.objects.create(name="API")
        context_window = ContextWindow.objects.create(name="32K")
        
        tool = Tool.objects.create(
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
        
        self.user.favourite_tools.add(tool)
        
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = SecureUserSerializer(
            self.user,
            context={'request': request}
        )
        
        self.assertEqual(len(serializer.data['favourite_tools']), 1)

    def test_create_user_with_secure_serializer(self):
        """Test creating a user with SecureUserSerializer"""
        request = self.factory.post('/')
        request.user = self.superuser
        
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com'
        }
        
        serializer = SecureUserSerializer(
            data=data,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpass123'))

    def test_password_is_write_only(self):
        """Test that password is write-only"""
        request = self.factory.get('/')
        request.user = self.user
        
        serializer = SecureUserSerializer(
            self.user,
            context={'request': request}
        )
        
        # Password should not appear in serialized output
        self.assertNotIn('password', serializer.data)

    def test_update_with_no_password(self):
        """Test updating user without changing password"""
        request = self.factory.patch('/')
        request.user = self.user
        
        old_password = self.user.password
        data = {'email': 'newemail@example.com'}
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        
        # Password should remain unchanged
        self.assertEqual(user.password, old_password)
        self.assertEqual(user.email, 'newemail@example.com')


class UserSerializerPermissionsTest(TestCase):
    """Test permission logic in user serializers"""

    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.staff = User.objects.create_user(
            username="staff",
            password="staff123",
            is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="admin123"
        )

    def test_field_permissions_for_regular_user(self):
        """Test field access for regular users"""
        request = self.factory.patch('/')
        request.user = self.user
        
        # Allowed fields
        allowed_data = {
            'email': 'test@example.com',
            'bio': 'Test bio'
        }
        
        serializer = SecureUserSerializer(
            self.user,
            data=allowed_data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid())

    def test_field_permissions_for_staff(self):
        """Test field access for staff users"""
        request = self.factory.patch('/')
        request.user = self.staff
        
        # Staff can modify more fields but not superuser fields
        data = {
            'email': 'test@example.com',
            'is_active': False
        }
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid())

    def test_field_permissions_for_superuser(self):
        """Test field access for superusers"""
        request = self.factory.patch('/')
        request.user = self.superuser
        
        # Superuser can modify all fields
        data = {
            'is_staff': True,
            'is_superuser': True,
            'is_active': False
        }
        
        serializer = SecureUserSerializer(
            self.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid())
