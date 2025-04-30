from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .apis import get_or_create_social_user
from .serializers import OAuthLoginSerializer


class OAuthLoginAPI(APIView):
    def post(self, request):
        serializer = OAuthLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        provider = serializer.validated_data["provider"]
        access_token = serializer.validated_data["access_token"]

        try:
            user, token_data = get_or_create_social_user(provider, access_token)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return Response(token_data)
