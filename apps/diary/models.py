from django.db import models

# from apps.user.models import User
# from apps.emotion.models import Emotion

class Diary(models.Model):
    # User ID (Foreign Key)
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     verbose_name='User ID'
    # )

    # Emotion ID (Foreign Key)
    # emotion = models.ForeignKey(
    #     Emotion,
    #     on_delete=models.CASCADE,
    #     verbose_name='Emotion ID'
    # )

    content = models.TextField(verbose_name='일기 내용')

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성 일자'
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 일자')

    visibility = models.BooleanField(
        default=False,
        verbose_name='공게/비공개'
    )

    class Meta:
        db_table = 'diary'
        verbose_name = '일기'
        verbose_name_plural = '일기 목록'