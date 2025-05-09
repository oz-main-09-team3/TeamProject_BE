from django.db import models

from users.models import User


class DiaryFriend(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    # 친구 요청자
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="send_friend")
    # 친구 수락자
    friend_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receive_friend"
    )
    # 'pending', 'accepted', 'rejected' 중 하나
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    # 요청일, 자동 생성
    requested_at = models.DateTimeField(auto_now_add=True)
    # 응답일, 선택적
    responded_at = models.DateTimeField(null=True, blank=True)

    # 예) user123 -> user456 (pending)
    def __str__(self):
        return f"{self.user} -> {self.friend_user_id} ({self.status})"
