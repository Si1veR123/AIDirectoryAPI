from django.test import TestCase
from django.contrib.auth import get_user_model
from tool.models import (
    Domain, Developer, Accessibility, ContextWindow, 
    Tool, RecommendationResults
)


class DomainModelTest(TestCase):
    """Test cases for Domain model"""

    def test_domain_creation(self):
        """Test creating a domain"""
        domain = Domain.objects.create(name="Machine Learning")
        self.assertEqual(domain.name, "Machine Learning")
        self.assertEqual(str(domain), "Machine Learning")

    def test_domain_primary_key(self):
        """Test that name is the primary key"""
        domain = Domain.objects.create(name="NLP")
        self.assertEqual(domain.pk, "NLP")


class DeveloperModelTest(TestCase):
    """Test cases for Developer model"""

    def test_developer_creation(self):
        """Test creating a developer"""
        developer = Developer.objects.create(name="OpenAI")
        self.assertEqual(developer.name, "OpenAI")
        self.assertEqual(str(developer), "OpenAI")

    def test_developer_primary_key(self):
        """Test that name is the primary key"""
        developer = Developer.objects.create(name="Anthropic")
        self.assertEqual(developer.pk, "Anthropic")


class AccessibilityModelTest(TestCase):
    """Test cases for Accessibility model"""

    def test_accessibility_creation(self):
        """Test creating an accessibility"""
        accessibility = Accessibility.objects.create(name="Web App")
        self.assertEqual(accessibility.name, "Web App")
        self.assertEqual(str(accessibility), "Web App")


class ContextWindowModelTest(TestCase):
    """Test cases for ContextWindow model"""

    def test_context_window_creation(self):
        """Test creating a context window"""
        context = ContextWindow.objects.create(name="128K tokens")
        self.assertEqual(context.name, "128K tokens")
        self.assertEqual(str(context), "128K tokens")


class ToolModelTest(TestCase):
    """Test cases for Tool model"""

    def setUp(self):
        """Set up test data"""
        self.developer = Developer.objects.create(name="TestDev")
        self.domain = Domain.objects.create(name="Testing")
        self.accessibility = Accessibility.objects.create(name="API")
        self.context_window = ContextWindow.objects.create(name="32K")

    def test_tool_creation(self):
        """Test creating a tool"""
        tool = Tool.objects.create(
            ai_name="TestAI",
            developer=self.developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Test functionality",
            pricing_model="Free",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            website_url="https://test.com"
        )
        self.assertEqual(tool.ai_name, "TestAI")
        self.assertEqual(tool.popularity_votes, 0)

    def test_tool_with_embedding(self):
        """Test tool with embedding data"""
        tool = Tool.objects.create(
            ai_name="EmbeddingAI",
            developer=self.developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            website_url="https://test.com",
            embedding=[0.1, 0.2, 0.3]
        )
        self.assertIsNotNone(tool.embedding)
        self.assertEqual(len(tool.embedding), 3)

    def test_tool_foreign_key_cascade(self):
        """Test that setting foreign keys to null works"""
        tool = Tool.objects.create(
            ai_name="CascadeAI",
            developer=self.developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            website_url="https://test.com"
        )
        
        # Delete developer and check that tool still exists
        self.developer.delete()
        tool.refresh_from_db()
        self.assertIsNone(tool.developer)


class RecommendationResultsModelTest(TestCase):
    """Test cases for RecommendationResults model"""

    def setUp(self):
        """Set up test data"""
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.developer = Developer.objects.create(name="TestDev")
        self.domain = Domain.objects.create(name="Testing")
        self.accessibility = Accessibility.objects.create(name="API")
        self.context_window = ContextWindow.objects.create(name="32K")
        
        self.tool = Tool.objects.create(
            ai_name="TestAI",
            developer=self.developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Test",
            pricing_model="Free",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            website_url="https://test.com"
        )

    def test_recommendation_creation(self):
        """Test creating a recommendation result"""
        result = RecommendationResults.objects.create(
            user=self.user,
            query="Find AI tools for coding"
        )
        self.assertEqual(result.user, self.user)
        self.assertEqual(result.query, "Find AI tools for coding")
        self.assertIsNotNone(result.started_at)
        self.assertIsNone(result.completed_at)
        self.assertIsNone(result.error)

    def test_recommendation_with_tools(self):
        """Test recommendation with recommended tools"""
        result = RecommendationResults.objects.create(
            user=self.user,
            query="Find AI tools"
        )
        result.recommended_tools.add(self.tool)
        self.assertEqual(result.recommended_tools.count(), 1)
        self.assertIn(self.tool, result.recommended_tools.all())

    def test_recommendation_cascade_delete(self):
        """Test that deleting user deletes recommendations"""
        result = RecommendationResults.objects.create(
            user=self.user,
            query="Test query"
        )
        user_id = self.user.id
        self.user.delete()
        
        # Check that recommendation was deleted
        self.assertFalse(
            RecommendationResults.objects.filter(user_id=user_id).exists()
        )
