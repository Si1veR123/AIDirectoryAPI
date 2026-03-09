from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from tool.models import (
    Domain, Developer, Accessibility, ContextWindow, Tool, RecommendationResults
)
from tool.serializers import (
    DeveloperSerializer, DomainSerializer, AccessibilitySerializer,
    ContextWindowSerializer, ToolSerializer, ToolNameSerializer,
    RecommendationRequestSerializer, RecommendationResponseSerializer,
    RecommendationResultsSerializer
)
from django.contrib.auth import get_user_model


class DeveloperSerializerTest(TestCase):
    """Test cases for DeveloperSerializer"""

    def test_serialize_developer(self):
        """Test serializing a developer"""
        developer = Developer.objects.create(name="OpenAI")
        serializer = DeveloperSerializer(developer)
        self.assertEqual(serializer.data['name'], 'OpenAI')

    def test_deserialize_developer(self):
        """Test deserializing developer data"""
        data = {'name': 'Anthropic'}
        serializer = DeveloperSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        developer = serializer.save()
        self.assertEqual(developer.name, 'Anthropic')


class DomainSerializerTest(TestCase):
    """Test cases for DomainSerializer"""

    def test_serialize_domain(self):
        """Test serializing a domain"""
        domain = Domain.objects.create(name="Machine Learning")
        serializer = DomainSerializer(domain)
        self.assertEqual(serializer.data['name'], 'Machine Learning')

    def test_deserialize_domain(self):
        """Test deserializing domain data"""
        data = {'name': 'NLP'}
        serializer = DomainSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        domain = serializer.save()
        self.assertEqual(domain.name, 'NLP')


class AccessibilitySerializerTest(TestCase):
    """Test cases for AccessibilitySerializer"""

    def test_serialize_accessibility(self):
        """Test serializing accessibility"""
        accessibility = Accessibility.objects.create(name="Web App")
        serializer = AccessibilitySerializer(accessibility)
        self.assertEqual(serializer.data['name'], 'Web App')


class ContextWindowSerializerTest(TestCase):
    """Test cases for ContextWindowSerializer"""

    def test_serialize_context_window(self):
        """Test serializing context window"""
        context = ContextWindow.objects.create(name="128K tokens")
        serializer = ContextWindowSerializer(context)
        self.assertEqual(serializer.data['name'], '128K tokens')


class ToolSerializerTest(TestCase):
    """Test cases for ToolSerializer"""

    def setUp(self):
        """Set up test data"""
        self.developer = Developer.objects.create(name="TestDev")
        self.domain = Domain.objects.create(name="Testing")
        self.accessibility = Accessibility.objects.create(name="API")
        self.context_window = ContextWindow.objects.create(name="32K")

    def test_serialize_tool(self):
        """Test serializing a tool"""
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
        serializer = ToolSerializer(tool)
        self.assertEqual(serializer.data['ai_name'], 'TestAI')
        self.assertEqual(serializer.data['developer'], 'TestDev')
        self.assertEqual(serializer.data['primary_domain'], 'Testing')
        self.assertNotIn('embedding', serializer.data)

    def test_deserialize_tool(self):
        """Test deserializing tool data"""
        data = {
            'ai_name': 'NewAI',
            'developer': self.developer.name,
            'release_year': 2024,
            'intelligence_type': 'Generative',
            'primary_domain': self.domain.name,
            'key_functionality': 'Testing',
            'pricing_model': 'Free',
            'api_availability': 'Yes',
            'context_window': self.context_window.name,
            'accessibility': self.accessibility.name,
            'website_url': 'https://newai.com'
        }
        serializer = ToolSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        tool = serializer.save()
        self.assertEqual(tool.ai_name, 'NewAI')
        self.assertEqual(tool.developer, self.developer)

    def test_tool_serializer_slug_field(self):
        """Test that slug fields work correctly"""
        tool = Tool.objects.create(
            ai_name="SlugTest",
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
        serializer = ToolSerializer(tool)
        # Check that related fields are serialized as names (strings)
        self.assertEqual(serializer.data['developer'], 'TestDev')
        self.assertIsInstance(serializer.data['developer'], str)


class ToolNameSerializerTest(TestCase):
    """Test cases for ToolNameSerializer"""

    def setUp(self):
        """Set up test data"""
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

    def test_serialize_tool_name(self):
        """Test serializing only tool name"""
        serializer = ToolNameSerializer(self.tool)
        self.assertEqual(serializer.data['ai_name'], 'TestAI')
        self.assertEqual(len(serializer.data), 1)


class RecommendationRequestSerializerTest(TestCase):
    """Test cases for RecommendationRequestSerializer"""

    def test_valid_request(self):
        """Test valid recommendation request"""
        data = {'q': 'Find AI tools for coding', 'top_n': 5}
        serializer = RecommendationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_request_without_query(self):
        """Test request without query fails"""
        data = {'top_n': 5}
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_request_with_default_top_n(self):
        """Test request uses default top_n"""
        data = {'q': 'Test query'}
        serializer = RecommendationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['top_n'], 5)

    def test_request_with_invalid_top_n(self):
        """Test request with invalid top_n"""
        data = {'q': 'Test query', 'top_n': 0}
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_request_with_max_top_n(self):
        """Test request with maximum top_n"""
        data = {'q': 'Test query', 'top_n': 100}
        serializer = RecommendationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_request_exceeding_max_top_n(self):
        """Test request exceeding maximum top_n"""
        data = {'q': 'Test query', 'top_n': 101}
        serializer = RecommendationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class RecommendationResponseSerializerTest(TestCase):
    """Test cases for RecommendationResponseSerializer"""

    def test_serialize_response(self):
        """Test serializing recommendation response"""
        data = {
            'detail': 'Recommendation created',
            'results_id': 1,
            'results_url_http': '/api/recommendations/1/',
            'results_url_ws': 'ws://localhost/ws/recommendations/1/'
        }
        serializer = RecommendationResponseSerializer(data)
        self.assertEqual(serializer.data['results_id'], 1)
        self.assertIn('results_url_http', serializer.data)


class RecommendationResultsSerializerTest(TestCase):
    """Test cases for RecommendationResultsSerializer"""

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

    def test_serialize_recommendation_results(self):
        """Test serializing recommendation results"""
        result = RecommendationResults.objects.create(
            user=self.user,
            query="Test query"
        )
        result.recommended_tools.add(self.tool)
        
        serializer = RecommendationResultsSerializer(result)
        self.assertEqual(serializer.data['query'], 'Test query')
        self.assertEqual(len(serializer.data['recommended_tools']), 1)
        self.assertEqual(
            serializer.data['recommended_tools'][0]['ai_name'],
            'TestAI'
        )

    def test_serialize_empty_results(self):
        """Test serializing results with no recommendations"""
        result = RecommendationResults.objects.create(
            user=self.user,
            query="Test query"
        )
        
        serializer = RecommendationResultsSerializer(result)
        self.assertEqual(len(serializer.data['recommended_tools']), 0)
