from django.contrib import admin

from friends.models import DiaryFriend


@admin.register(DiaryFriend)
class FriendAdmin(admin.ModelAdmin):
    # 리스트 화면에 보여줄 필드
    list_display = [
        "id",
        "user",
        "get_friend_username",
        "status",
        "requested_at",
        "responded_at",
    ]
    # 오른쪽 필터 사이드바이 표시
    list_filter = ["status", "requested_at"]
    # 검색창에서 사용될 필드 (__username은 외래키 연결된 User의 username 기준)
    search_fields = ["user__username", "friend_user_id__username"]
    # 최신 요청일 순으로 정렬
    ordering = ("-requested_at",)

    def get_friend_username(self, obj):
        return obj.friend_user_id.username  # <- 필드명 변경

    get_friend_username.short_description = "친구 사용자명"
