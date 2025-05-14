# views.py

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .apis import accept_friend_request, invite_friend, reject_friend_request
from .serializers import (
    DiaryFriendSerializer,
    FriendInviteRequestSerializer,
)


class FriendInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FriendInviteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friend_user_id = serializer.validated_data["friend_user_id"]
        diary_friend, error = invite_friend(request.user, friend_user_id)
        if error:
            return Response({"message": error}, status=400)
        return Response(DiaryFriendSerializer(diary_friend).data, status=201)


class FriendAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, friend_id):
        diary_friend, error = accept_friend_request(friend_id, request.user)
        if error:
            return Response({"message": error}, status=404)
        return Response(DiaryFriendSerializer(diary_friend).data)


class FriendRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, friend_id):
        diary_friend, error = reject_friend_request(friend_id, request.user)
        if error:
            return Response({"message": error}, status=404)
        return Response(DiaryFriendSerializer(diary_friend).data)
