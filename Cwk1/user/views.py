from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from .serializers import SecureUserSerializer
from rest_framework import permissions

class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SecureUserSerializer
    permission_classes = [permissions.AllowAny]

class CurrentUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SecureUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetailViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = SecureUserSerializer
    permission_classes = [permissions.IsAdminUser]