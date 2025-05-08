from django.urls import path
from rest_framework.routers import DefaultRouter

from emotion.apis import (
    EmotionCountView,
    EmotionTrendView,
    EmotionViewSet,
)

router = DefaultRouter()
router.register(r"", EmotionViewSet, basename="emotions")

urlpatterns = router.urls + [
    path("trend/", EmotionTrendView.as_view(), name="emotion_trend"),
    path("count/", EmotionCountView.as_view(), name="emotion_count"),
]
