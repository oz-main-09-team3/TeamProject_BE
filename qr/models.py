from django.db import models
from users.models import User

class QrCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invite_code = models.CharField(max_length=64, verbose_name="초대코드")

    def __str__(self):
        return f"{self.user} - {self.invite_code}"
