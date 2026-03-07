from rest_framework import generics
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth import get_user_model
from .serializers import SecureUserSerializer
from tool.serializers import ToolNameSerializer
from tool.models import Tool
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema(tags=['Register'], description="Endpoint for user registration. Open to all users.")
class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SecureUserSerializer
    permission_classes = [AllowAny]

@extend_schema(tags=['Current User'], description="Retrieve, update, or delete the current user's profile. Authenticated users only.")
class CurrentUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SecureUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

@extend_schema(tags=['Admin User Management'],
description="REST endpoints for users. Only staff can access these endpoints."
)
class UserViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = SecureUserSerializer
    permission_classes = [IsAdminUser]

@extend_schema(
    tags=['Favourites'], 
    description="Manage favourite tools for current user. Endpoints take the ai_name field of the Tool."
)
class CurrentUserFavouriteToolViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ToolNameSerializer

    def get_user(self):
        return self.request.user

    def list(self, request):
        user = self.get_user()
        serializer = ToolNameSerializer(user.favourite_tools.all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.get_user()

        serializer = ToolNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tool = serializer.validated_data["ai_name"]
        tool = get_object_or_404(Tool, ai_name=tool)
        user.favourite_tools.add(tool)

        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, ai_name=None):
        user = self.get_user()

        tool = get_object_or_404(Tool, ai_name=ai_name)
        user.favourite_tools.remove(tool)

        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    tags=['Favourites'], 
    description="Manage favourite tools for any user. Staff only."
)
class UserFavouriteToolViewSet(CurrentUserFavouriteToolViewSet):
    permission_classes = [IsAdminUser]

    def get_user(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(get_user_model(), pk=user_id)
        return user