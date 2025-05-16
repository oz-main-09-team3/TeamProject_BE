from django.urls import path
from rest_framework.routers import DefaultRouter

from qr.apis import QrCodeCreateView

urlpatterns = [
    path("", QrCodeCreateView.as_view(), name="qrcode"),
]
