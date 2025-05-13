import os

from django.db import IntegrityError
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
            # 🔐 소셜 access_token 및 사용자 정보 가져오기
            oauth_client = OAuth2Client(provider, code, redirect_uri)
            access_token, user_info = oauth_client.get_token_and_user_info()

            # 📌 username 생성
            provider_user_id = user_info["id"]
            username = f"{provider}{provider_user_id}"

            # 👤 유저 생성 또는 가져오기 (중복 시 예외 처리)
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "nickname": user_info.get("nickname", ""),
                        "profile": user_info.get("profile_img", None),
                    }
                )
            except IntegrityError:
                user = User.objects.get(username=username)

            # 🔗 SocialAccount 연결
            social_account, _ = SocialAccount.objects.get_or_create(
                provider=provider,
                provider_user_id=provider_user_id,
                defaults={"user": user},
            )

            user = social_account.user  # 혹시라도 연결된 다른 유저가 있다면 보정

            # 🔑 JWT 발급
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": UserSerializer(user).data,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
