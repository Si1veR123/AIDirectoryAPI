from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import Tool, Developer, Domain, Accessibility, ContextWindow
from .serializers import ToolSerializer, DeveloperSerializer, DomainSerializer, AccessibilitySerializer, ContextWindowSerializer

# Create your views here.
class DeveloperViewSet(ReadOnlyModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer

class DomainViewSet(ReadOnlyModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

class AccessibilityViewSet(ReadOnlyModelViewSet):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer

class ContextWindowViewSet(ReadOnlyModelViewSet):
    queryset = ContextWindow.objects.all()
    serializer_class = ContextWindowSerializer

class ToolViewSet(ReadOnlyModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
