from django.urls import path
from rest_framework.routers import DefaultRouter

from emotion.apis import EmotionViewSet, EmotionTrendView, EmotionCountView

router = DefaultRouter()
router.register(r'emotions', EmotionViewSet, basename='emotions')

urlpatterns = router.urls + [
    path("emotion/trend/", EmotionTrendView.as_view(), name="emotion_trend"),
    path("emotion/count/", EmotionCountView.as_view(), name="emotion_count"),
]