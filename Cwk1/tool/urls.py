from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ToolViewSet, DeveloperViewSet, DomainViewSet, AccessibilityViewSet, ContextWindowViewSet

router = DefaultRouter()
router.register(r'developers', DeveloperViewSet, basename='developer')
router.register(r'domains', DomainViewSet, basename='domain')
router.register(r'accessibilities', AccessibilityViewSet, basename='accessibility')
router.register(r'context-windows', ContextWindowViewSet, basename='context-window')
router.register(r'', ToolViewSet, basename='tool')
urlpatterns = [
    path('', include(router.urls)),
]
