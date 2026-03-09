from django.test import TestCase
from django.contrib.auth import get_user_model
from user.models import CustomUser
from tool.models import Domain, Developer, Accessibility, ContextWindow, Tool


class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model"""

    def setUp(self):
        """Set up test data"""
        self.domain = Domain.objects.create(name="Machine Learning")
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def test_user_creation(self):
        """Test creating a user"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_with_interested_domain(self):
        """Test user with interested domain"""
        self.user.interested_domain = self.domain
        self.user.save()
        self.assertEqual(self.user.interested_domain, self.domain)

    def test_user_email_alerts_default(self):
        """Test that email_alerts defaults to False"""
        self.assertFalse(self.user.email_alerts)

    def test_user_email_alerts_enabled(self):
        """Test enabling email alerts"""
        self.user.email_alerts = True
        self.user.save()
        self.assertTrue(self.user.email_alerts)

    def test_user_date_of_birth(self):
        """Test setting date of birth"""
        from datetime import date
        dob = date(1990, 1, 1)
        self.user.date_of_birth = dob
        self.user.save()
        self.assertEqual(self.user.date_of_birth, dob)

    def test_user_bio(self):
        """Test setting user bio"""
        bio = "This is a test bio"
        self.user.bio = bio
        self.user.save()
        self.assertEqual(self.user.bio, bio)

    def test_user_favourite_tools(self):
        """Test adding favourite tools"""
        # Create tool
        developer = Developer.objects.create(name="TestDev")
        accessibility = Accessibility.objects.create(name="API")
        context_window = ContextWindow.objects.create(name="32K")
        
        tool = Tool.objects.create(
            ai_name="TestAI",
            developer=developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=context_window,
            accessibility=accessibility,
            website_url="https://test.com"
        )
        
        self.user.favourite_tools.add(tool)
        self.assertEqual(self.user.favourite_tools.count(), 1)
        self.assertIn(tool, self.user.favourite_tools.all())

    def test_user_multiple_favourite_tools(self):
        """Test adding multiple favourite tools"""
        developer = Developer.objects.create(name="TestDev")
        accessibility = Accessibility.objects.create(name="API")
        context_window = ContextWindow.objects.create(name="32K")
        
        tool1 = Tool.objects.create(
            ai_name="Tool1",
            developer=developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=context_window,
            accessibility=accessibility,
            website_url="https://test1.com"
        )
        
        tool2 = Tool.objects.create(
            ai_name="Tool2",
            developer=developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=context_window,
            accessibility=accessibility,
            website_url="https://test2.com"
        )
        
        self.user.favourite_tools.add(tool1, tool2)
        self.assertEqual(self.user.favourite_tools.count(), 2)

    def test_domain_cascade_on_delete(self):
        """Test that deleting domain sets user's interested_domain to null"""
        self.user.interested_domain = self.domain
        self.user.save()
        
        self.domain.delete()
        self.user.refresh_from_db()
        self.assertIsNone(self.user.interested_domain)

    def test_user_str_method(self):
        """Test string representation uses username"""
        self.assertEqual(str(self.user), "testuser")

    def test_superuser_creation(self):
        """Test creating a superuser"""
        User = get_user_model()
        superuser = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@example.com"
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_user_optional_fields_blank(self):
        """Test that optional fields can be blank"""
        User = get_user_model()
        user = User.objects.create_user(
            username="minimal",
            password="pass123"
        )
        self.assertIsNone(user.interested_domain)
        self.assertIsNone(user.date_of_birth)
        self.assertIsNone(user.bio)
        self.assertEqual(user.favourite_tools.count(), 0)
