from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=30, blank=True)
    phone_num = models.CharField(max_length=20, blank=True)
    profile_img = models.ImageField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class SocialAccount(models.Model):
    social_account_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_account")
    provider = models.CharField(max_length=20) # 네이버, 구글, 카카오 등
    provider_user_id = models.CharField(max_length=100) # 네이버, 구글, 카카오 에서의 id

    def __str__(self):
        return f"{self.provider} - {self.provider_user_id}"