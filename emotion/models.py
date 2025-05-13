from django.db import models


class Emotion(models.Model):
    emoji = models.CharField(
        max_length=255,
        verbose_name="감자 이모지 url",
        help_text="예: 1.png",
    )
    emotion = models.CharField(max_length=10, verbose_name="감정", blank=True)

    def __str__(self):
        return f"{self.emoji} - {self.emotion}"

    @property
    def image_url(self):
        return f"/static/emotions/{self.emoji}"


class EmotionData(models.Model):
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "감정 사용 기록"
        verbose_name_plural = "감정 사용 기록들"

    def __str__(self):
        return f'{self.emotion} 사용됨 at {self.created_at.strftime("%Y-%m-%d %H:%M")}'
