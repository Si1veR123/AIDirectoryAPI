from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tool.models import (
    Domain, Developer, Accessibility, ContextWindow, 
    Tool, RecommendationResults
)


class DeveloperViewSetTest(TestCase):
    """Test cases for DeveloperViewSet"""

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
        self.developer = Developer.objects.create(name="OpenAI")

    def test_list_developers_unauthenticated(self):
        """Test that unauthenticated users can list developers"""
        response = self.client.get('/api/tools/developers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_developer_as_staff(self):
        """Test that staff can create developers"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/tools/developers/', {'name': 'Anthropic'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Developer.objects.filter(name='Anthropic').exists())

    def test_create_developer_as_regular_user(self):
        """Test that regular users cannot create developers"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/tools/developers/', {'name': 'TestDev'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_developer(self):
        """Test retrieving a single developer"""
        response = self.client.get(f'/api/tools/developers/{self.developer.name}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'OpenAI')

    def test_update_developer_as_staff(self):
        """Test that staff can update developers"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f'/api/tools/developers/{self.developer.name}/',
            {'name': 'OpenAI Updated'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_developer_as_staff(self):
        """Test that staff can delete developers"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/tools/developers/{self.developer.name}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Developer.objects.filter(name='OpenAI').exists())


class DomainViewSetTest(TestCase):
    """Test cases for DomainViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )
        self.domain = Domain.objects.create(name="Machine Learning")

    def test_list_domains_unauthenticated(self):
        """Test that unauthenticated users can list domains"""
        response = self.client.get('/api/tools/domains/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_domain_as_staff(self):
        """Test that staff can create domains"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/tools/domains/', {'name': 'NLP'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ToolViewSetTest(TestCase):
    """Test cases for ToolViewSet"""

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
        
        # Create related objects
        self.developer = Developer.objects.create(name="TestDev")
        self.domain = Domain.objects.create(name="Testing")
        self.accessibility = Accessibility.objects.create(name="Web App")
        self.context_window = ContextWindow.objects.create(name="32K")
        
        # Create tools
        self.tool1 = Tool.objects.create(
            ai_name="GPT-4",
            developer=self.developer,
            release_year=2023,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Text generation",
            pricing_model="Paid",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            popularity_votes=1000,
            website_url="https://test1.com"
        )
        
        self.tool2 = Tool.objects.create(
            ai_name="Claude",
            developer=self.developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain,
            key_functionality="Conversation",
            pricing_model="Freemium",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            popularity_votes=500,
            website_url="https://test2.com"
        )

    def test_list_tools_unauthenticated(self):
        """Test that unauthenticated users can list tools"""
        response = self.client.get('/api/tools/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_tools_pagination(self):
        """Test tool list pagination"""
        response = self.client.get('/api/tools/?page=1&page_size=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_tool(self):
        """Test retrieving a single tool"""
        response = self.client.get(f'/api/tools/{self.tool1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ai_name'], 'GPT-4')

    def test_create_tool_as_staff(self):
        """Test that staff can create tools"""
        self.client.force_authenticate(user=self.admin)
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
        response = self.client.post('/api/tools/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_tool_as_regular_user(self):
        """Test that regular users cannot create tools"""
        self.client.force_authenticate(user=self.user)
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
        response = self.client.post('/api/tools/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_tool_as_staff(self):
        """Test that staff can update tools"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'ai_name': 'GPT-4 Updated',
            'developer': self.developer.name,
            'release_year': 2023,
            'intelligence_type': 'Generative',
            'primary_domain': self.domain.name,
            'key_functionality': 'Updated functionality',
            'pricing_model': 'Paid',
            'api_availability': 'Yes',
            'context_window': self.context_window.name,
            'accessibility': self.accessibility.name,
            'website_url': 'https://test1.com'
        }
        response = self.client.put(f'/api/tools/{self.tool1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_tool_as_staff(self):
        """Test that staff can delete tools"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/tools/{self.tool1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ToolSearchViewSetTest(TestCase):
    """Test cases for ToolSearchViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create related objects
        self.developer = Developer.objects.create(name="TestDev")
        self.domain1 = Domain.objects.create(name="NLP")
        self.domain2 = Domain.objects.create(name="Vision")
        self.accessibility = Accessibility.objects.create(name="API")
        self.context_window = ContextWindow.objects.create(name="32K")
        
        # Create tools
        self.tool1 = Tool.objects.create(
            ai_name="GPT-4 Vision",
            developer=self.developer,
            release_year=2023,
            intelligence_type="Generative",
            primary_domain=self.domain1,
            key_functionality="Text and image processing",
            pricing_model="Paid",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            popularity_votes=1000,
            website_url="https://test1.com"
        )
        
        self.tool2 = Tool.objects.create(
            ai_name="DALL-E",
            developer=self.developer,
            release_year=2024,
            intelligence_type="Generative",
            primary_domain=self.domain2,
            key_functionality="Image generation",
            pricing_model="Freemium",
            api_availability="Yes",
            context_window=self.context_window,
            accessibility=self.accessibility,
            popularity_votes=500,
            website_url="https://test2.com"
        )

    def test_search_by_name(self):
        """Test searching tools by name"""
        response = self.client.get('/api/tools/search/?q=vision')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ai_name'], 'GPT-4 Vision')

    def test_filter_by_domain(self):
        """Test filtering tools by domain"""
        response = self.client.get(f'/api/tools/search/?primary_domain={self.domain2.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ai_name'], 'DALL-E')

    def test_filter_by_popularity_range(self):
        """Test filtering by popularity vote range"""
        response = self.client.get('/api/tools/search/?popularity_votes-min=600')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ai_name'], 'GPT-4 Vision')

    def test_sort_by_popularity_desc(self):
        """Test sorting by popularity votes descending"""
        response = self.client.get('/api/tools/search/?sort-by=popularity_votes&order=desc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ai_name'], 'GPT-4 Vision')
        self.assertEqual(response.data[1]['ai_name'], 'DALL-E')

    def test_search_with_pagination(self):
        """Test search with pagination"""
        response = self.client.get('/api/tools/search/?page=1&page_size=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_combined_filters(self):
        """Test combining multiple filters"""
        response = self.client.get(
            '/api/tools/search/?release_year=2024&pricing_model=Freemium'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ai_name'], 'DALL-E')


class RecommendToolViewSetTest(TestCase):
    """Test cases for RecommendToolViewSet"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass123"
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )

    def test_create_recommendation_authenticated(self):
        """Test creating recommendation as authenticated user"""
        self.client.force_authenticate(user=self.user)
        data = {'q': 'AI tools for coding', 'top_n': 5}
        response = self.client.post('/api/tools/recommend/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('results_id', response.data)
        self.assertIn('results_url_http', response.data)

    def test_create_recommendation_unauthenticated(self):
        """Test that unauthenticated users cannot create recommendations"""
        data = {'q': 'AI tools for coding'}
        response = self.client.post('/api/tools/recommend/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_recommendation_without_query(self):
        """Test creating recommendation without query fails"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/tools/recommend/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_own_recommendation(self):
        """Test retrieving own recommendation results"""
        self.client.force_authenticate(user=self.user)
        result = RecommendationResults.objects.create(
            user=self.user,
            query="Test query"
        )
        response = self.client.get(f'/api/tools/recommend/{result.id}/')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_retrieve_other_users_recommendation(self):
        """Test that users cannot retrieve other users' recommendations"""
        self.client.force_authenticate(user=self.user)
        result = RecommendationResults.objects.create(
            user=self.other_user,
            query="Test query"
        )
        response = self.client.get(f'/api/tools/recommend/{result.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_retrieve_any_recommendation(self):
        """Test that admin can retrieve any recommendation"""
        self.client.force_authenticate(user=self.admin)
        result = RecommendationResults.objects.create(
            user=self.other_user,
            query="Test query"
        )
        response = self.client.get(f'/api/tools/recommend/{result.id}/')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_delete_own_recommendation(self):
        """Test deleting own recommendation"""
        self.client.force_authenticate(user=self.user)
        result = RecommendationResults.objects.create(
            user=self.user,
            query="Test query"
        )
        response = self.client.delete(f'/api/tools/recommend/{result.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_users_recommendation(self):
        """Test that users cannot delete other users' recommendations"""
        self.client.force_authenticate(user=self.user)
        result = RecommendationResults.objects.create(
            user=self.other_user,
            query="Test query"
        )
        response = self.client.delete(f'/api/tools/recommend/{result.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_recommendations_as_user(self):
        """Test listing recommendations as regular user"""
        self.client.force_authenticate(user=self.user)
        RecommendationResults.objects.create(user=self.user, query="Query 1")
        RecommendationResults.objects.create(user=self.other_user, query="Query 2")
        
        response = self.client.get('/api/tools/recommend/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User should only see their own recommendations
        self.assertEqual(len(response.data), 1)

    def test_list_recommendations_as_admin(self):
        """Test listing recommendations as admin"""
        self.client.force_authenticate(user=self.admin)
        RecommendationResults.objects.create(user=self.user, query="Query 1")
        RecommendationResults.objects.create(user=self.other_user, query="Query 2")
        
        response = self.client.get('/api/tools/recommend/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin should see all recommendations
        self.assertEqual(len(response.data), 2)
