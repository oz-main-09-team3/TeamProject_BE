# models.py
from django.conf import settings
from django.db import models

from emotion.models import Emotion
from users.models import User


class Diary(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    content = models.TextField(verbose_name="일기 내용")

    visibility = models.BooleanField(
        default=False,
        verbose_name="공게/비공개",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 일자",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정 일자",
    )

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"일기 {self.id}"


class DiaryImage(models.Model):
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, related_name="images", verbose_name="Diary ID"
    )
    image = models.FileField(
        upload_to="diary_images/",
        null=True,
        blank=True,
        verbose_name="Image File",  # S3 경로 지정
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for Diary {self.diary.id}"


# Emotion은 사전 정의된 감정 목록이며, 일기와의 연결을 별도 모델로 관리해야 함.
class DiaryEmotion(models.Model):
    diary = models.OneToOneField(
        Diary, on_delete=models.CASCADE, related_name="emotion"
    )

    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)


class Comment(models.Model):
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name="comments")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class Like(models.Model):
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name="likes")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
