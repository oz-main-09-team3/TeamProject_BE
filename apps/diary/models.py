from django.db import models

# from apps.user.models import User

class Diary(models.Model):
    # User ID (Foreign Key)
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     verbose_name='User ID',
    # )

    content = models.TextField(verbose_name='일기 내용')

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성 일자',
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 일자',)

    visibility = models.BooleanField(
        default=False,
        verbose_name='공게/비공개',
    )

    def __str__(self):
        return f'일기 {self.id}'

class DiaryImage(models.Model):
    # TODO: image_url → S3 연동 필요
    diary = models.ForeignKey(
        Diary,
        on_delete=models.CASCADE,
        verbose_name='Diary ID',
    )

    image_url = models.CharField(
        max_length=255,
        verbose_name='Image URL',
    )

    def __str__(self):
        return f'Image for Diary {self.diary.id}'

class Emotion(models.Model):
    diary = models.ForeignKey(
        Diary,
        on_delete=models.CASCADE,
        verbose_name='Diary ID',
    )
    emoji = models.CharField(
        max_length=255,
        verbose_name='감자 이모지 url',
    )
    emotion = models.CharField(
        max_length=10,
        verbose_name='감정',
    )

    def __str__(self):
        return f'Emotion {self.emotion} for Diary {self.diary.id}'