from django.db import models

from users.models import User


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 유저 FK(수신자)
    type = models.CharField(max_length=20, verbose_name="알림 종류")  # 알림 타입
    message = models.CharField(
        max_length=255, verbose_name="알림 메시지"
    )  # 알림 메시지
    is_read = models.BooleanField(
        default=False, verbose_name="읽음 여부"
    )  # 읽음 여부(처음 알림이 생성될 땐 읽지 않은 상태이므로 False로 기본값 설정)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="생성일"
    )  # 생성 일시

    def __str__(self):
        return f"{self.user} - {self.type} - {self.message}"
