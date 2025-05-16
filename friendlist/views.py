from django.db.models import Q
from rest_framework import (
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from friends.models import DiaryFriend

from .apis import get_friends_by_status
from .serializers import FriendListSerializer


class FriendListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        status_param = request.query_params.get("status", "accepted")
        if status_param not in ["pending", "accepted", "rejected"]:
            return Response(
                {
                    "detail": "Invalid status parameter. Choose pending, accepted, or rejected."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_users = get_friends_by_status(request.user, status_param)
        serializer = FriendListSerializer(friend_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, friend_id: int):
        # accepted 상태의 양방향 관계만 삭제
        delete_queryset = DiaryFriend.objects.filter(
            (
                Q(user=request.user, friend_user_id=friend_id)
                | Q(user_id=friend_id, friend_user_id=request.user)
            )
            & Q(status="accepted")
        )
        if not delete_queryset.exists():
            return Response(
                {"detail": "삭제할 친구 관계가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        delete_queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
