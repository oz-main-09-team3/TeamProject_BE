from django.db import models


class Qr(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
