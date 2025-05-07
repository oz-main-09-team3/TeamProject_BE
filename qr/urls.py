from django.urls import path
from rest_framework.routers import DefaultRouter

from qr.apis import QrCodeView

urlpatterns = [
    path("qrcode/", QrCodeView.as_view(), name="qrcode"),
]
