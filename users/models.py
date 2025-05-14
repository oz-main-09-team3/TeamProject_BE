from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    birthday = models.DateField(null=True, blank=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    profile = models.ImageField(
        max_length=1024, upload_to="profiles/", null=True, blank=True
    )
    phone_num = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class SocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    provider = models.CharField(max_length=255)  # kakao, google, naver
    provider_user_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ("provider", "provider_user_id")


# 제발.... 제발....
