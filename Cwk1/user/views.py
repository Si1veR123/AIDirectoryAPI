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
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema

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

@extend_schema(tags=['Favourites'], 
description="""Manage favourite tools for users. Endpoints take the ai_name field of the Tool.
- Normal users can only manage their own favourites.
- Staff users can manage favourites for any user.""")
class FavouriteToolViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ToolNameSerializer

    def get_user(self):
        user_id = self.kwargs.get("user_id")

        # /user/current/favourites
        if user_id is None:
            return self.request.user

        # /user/{id}/favourites
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can access other users")

        return get_object_or_404(get_user_model(), pk=user_id)

    def list(self, request):
        user = self.get_user()
        serializer = ToolNameSerializer(user.favourite_tools.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ToolNameSerializer,
        responses={201: None},
        description="Add a tool to favourites."
    )
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