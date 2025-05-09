from django.urls import path
from rest_framework.routers import DefaultRouter

from emotion.apis import (
    EmotionStatisticsView,
    EmotionTrendView,
    EmotionViewSet,
)

router = DefaultRouter()
router.register(r"", EmotionViewSet, basename="emotions")

urlpatterns = [
    path("trend/", EmotionTrendView.as_view(), name="emotion_trend"),
    path("count/", EmotionStatisticsView.as_view(), name="emotion_count"),
] + router.urls
