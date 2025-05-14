from django.urls import path

from .views import FriendAcceptView, FriendInviteView, FriendRejectView

urlpatterns = [
    path("invite/", FriendInviteView.as_view(), name="friend-invite"),
    path("<int:friend_id>/accept/", FriendAcceptView.as_view(), name="friend-accept"),
    path("<int:friend_id>/reject/", FriendRejectView.as_view(), name="friend-reject"),
]
