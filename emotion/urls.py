from django.urls import path
from rest_framework.routers import DefaultRouter

from emotion.apis import EmotionCountView, EmotionTrendView, EmotionViewSet, EmotionListView

router = DefaultRouter()
router.register(r"emotions", EmotionViewSet, basename="emotions")

urlpatterns = router.urls + [
    path("emotion/trend/", EmotionTrendView.as_view(), name="emotion_trend"),
    path("emotion/count/", EmotionCountView.as_view(), name="emotion_count"),
    path("emotion/", EmotionListView.as_view(), name="emotion_list"),
]
