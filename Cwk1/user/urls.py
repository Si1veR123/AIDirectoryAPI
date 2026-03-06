from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user.views import RegisterView, CurrentUserDetailView, UserViewSet, FavouriteToolViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),

    path('current/', CurrentUserDetailView.as_view()),

    path('', include(router.urls)),

    path(
        'user/current/favourites/',
        FavouriteToolViewSet.as_view({'get': 'list', 'post': 'create'})
    ),

    path(
        'user/current/favourites/<str:ai_name>/',
        FavouriteToolViewSet.as_view({'delete': 'destroy'})
    ),

    path(
        '<int:user_id>/favourites/',
        FavouriteToolViewSet.as_view({'get': 'list', 'post': 'create'})
    ),

    path(
        '<int:user_id>/favourites/<str:ai_name>/',
        FavouriteToolViewSet.as_view({'delete': 'destroy'})
    ),
]