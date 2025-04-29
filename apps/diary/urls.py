from django.urls import path

from apps.diary.views import DiaryView, DiaryCalendarView, DiaryByDateView

urlpatterns = [
    path('', DiaryView.as_view()),
    path('<int:diary_id>/', DiaryView.as_view()),

    # 달력형 일기 목록 조회
    path('calendar/', DiaryCalendarView.as_view()),

    # 특정 날짜의 일기 목록 조회
    path('date/<str:date>/', DiaryByDateView.as_view()),
]
