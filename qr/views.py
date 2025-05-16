# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from friends.serializers import DiaryFriendSerializer
from .apis import add_friend_by_qr

class QrFriendInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        invite_code = request.data.get("invite_code")
        if not invite_code:
            return Response({"message": "invite_code가 필요합니다."}, status=400)
        diary_friend, error = add_friend_by_qr(invite_code, request.user)
        if error:
            return Response({"message": error}, status=400)
        return Response(DiaryFriendSerializer(diary_friend).data, status=201)