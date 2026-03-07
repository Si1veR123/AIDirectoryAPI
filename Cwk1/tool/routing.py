from django.urls import re_path
from .consumers import RecommendationConsumer

urlpatterns = [
    re_path(r"^ws/recommend/(?P<results_id>\d+)/$", RecommendationConsumer.as_asgi(), name='recommendation-results-ws'),
]