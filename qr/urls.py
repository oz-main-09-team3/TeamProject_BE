from django.urls import path
from rest_framework.routers import DefaultRouter

from qr.apis import QrCodeCreateView
from qr.views import QrFriendInviteView

urlpatterns = [
    path("", QrCodeCreateView.as_view(), name="qrcode"),
    path("qr-invite/", QrFriendInviteView.as_view(), name="qr-friend-invite"),
]
