# models.py
from django.conf import settings
from django.db import models

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
    # TODO: image_url → S3 연동 필요
    diary = models.ForeignKey(
        Diary, on_delete=models.CASCADE, verbose_name="Diary ID", related_name="images"
    )

    image_url = models.CharField(
        max_length=255,
        verbose_name="Image URL",
    )

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for Diary {self.diary.id}"


class Emotion(models.Model):
    emoji = models.CharField(
        max_length=255,
        verbose_name="감자 이모지 url",
    )
    emotion = models.CharField(
        max_length=10,
        verbose_name="감정",
    )

    def __str__(self):
        return f"Emotion {self.emotion}"


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
