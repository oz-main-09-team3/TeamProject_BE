from django.urls import path
from rest_framework.routers import DefaultRouter
from qr.apis import QrCodeView

router = DefaultRouter()
router.register(r"qrcode", QrCodeView, basename="qrcode")

urlpatterns = router.urls