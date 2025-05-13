from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .apis import get_friend_list, delete_friend
from .serializers import FriendListSerializer

class FriendListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        friends = get_friend_list(request.user)
        serializer = FriendListSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FriendDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, friend_id):
        delete_friend(request.user, friend_id)
        return Response(status=status.HTTP_204_NO_CONTENT)