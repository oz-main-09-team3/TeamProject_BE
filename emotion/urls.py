from django.urls import path

from emotion.apis import (
    EmotionListView,
    EmotionStatisticsView,
    EmotionTrendView,
)

urlpatterns = [
    path("", EmotionListView.as_view(), name="emotion_list"),
    path("trend/", EmotionTrendView.as_view(), name="emotion_trend"),
    path("count/", EmotionStatisticsView.as_view(), name="emotion_count"),
]
