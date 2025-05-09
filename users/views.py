from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .apis import OAuth2Client
from .models import SocialAccount, User
from .serializers import OAuthLoginSerializer, UserMeSerializer, UserSerializer


class OAuthLoginView(APIView):
    def post(self, request, provider):
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        redirect_uri = request.data.get("redirect_uri")

        try:
            oauth_client = OAuth2Client(provider, code, redirect_uri)
            access_token, user_info = oauth_client.get_token_and_user_info()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user_id = user_info["id"]
        # 소셜 계정 존재 여부 확인 및 유저 생성
        social_account, created = SocialAccount.objects.get_or_create(
            provider=provider,
            provider_user_id=user_id,
            defaults={
                "user": User.objects.create(
                    username=f"{provider}_{user_id}",
                    nickname=user_info.get("nickname"),
                    profile=user_info.get("profile_img"),
                )
            },
        )
        user = social_account.user

        # JWT 발급
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class UserMeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)

    def patch(self, request):
        serializer = UserMeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserMeSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)
