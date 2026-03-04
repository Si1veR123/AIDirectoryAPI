from rest_framework.viewsets import ModelViewSet
from .models import Tool, Developer, Domain, Accessibility, ContextWindow
from .serializers import ToolSerializer, DeveloperSerializer, DomainSerializer, AccessibilitySerializer, ContextWindowSerializer

# Create your views here.
class DeveloperViewSet(ModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer

class DomainViewSet(ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

class AccessibilityViewSet(ModelViewSet):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer

class ContextWindowViewSet(ModelViewSet):
    queryset = ContextWindow.objects.all()
    serializer_class = ContextWindowSerializer

class ToolViewSet(ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
