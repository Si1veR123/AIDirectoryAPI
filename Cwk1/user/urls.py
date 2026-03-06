from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user.views import RegisterView, CurrentUserDetailView, UserDetailViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'manage', UserDetailViewSet, basename='user-manage')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('current/', CurrentUserDetailView.as_view(), name='current_user'),
    path('', include(router.urls))
]
