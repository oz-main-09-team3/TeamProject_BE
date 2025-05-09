from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)  # 기본 Django 관리자(admin) 페이지에 등록
class NotificationAdmin(admin.ModelAdmin):
    # 관리자 목록 화면에서 보여줄 열(column)들을 설정
    list_display = ["id", "user", "type", "message", "created_at"]
    # 관리자가 검색창을 통해 검색할 수 있게 해주는 필드 지정
    # user_username: ForeignKey로 연결된 User 모델의 username 필드를 의미(유저 이름으로 알림을 검색)
    search_fields = ["user__username"]
    # 필터 사이드바를 만들어 줌(알림 생성일을 기준을 필터링할 수 있는 옵션이 관리자 페이지에 생성)
    list_filter = ["created_at"]
