from rest_framework.viewsets import ModelViewSet
from .models import Tool
from .serializers import ToolSerializer

# Create your views here.
class ToolViewSet(ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
