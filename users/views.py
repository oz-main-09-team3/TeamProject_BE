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
            oauth_client = OAuth2Client(provider, code, redirect_uri)
            access_token, user_info = oauth_client.get_token_and_user_info()

            try:
                user, _ = User.objects.get_or_create(
                    username=f"{provider}{user_info['id']}",
                    defaults={
                        "nickname": user_info.get("nickname", ""),
                        "profile": user_info.get("profile_img", None),
                    },
                )
            except IntegrityError:
                # 이미 존재하는 경우, 기존 사용자 불러오기
                user = User.objects.get(username=f"{provider}{user_info['id']}")

            social_account, created = SocialAccount.objects.get_or_create(
                provider=provider,
                provider_user_id=(provider_user_id := user_info["id"]),
                defaults={"user": user},
            )
            print(
                f"🔎 provider_user_id 길이: {len(provider_user_id)} / 값: {provider_user_id}",
                flush=True,
            )
            user = social_account.user

            # JWT 발급
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
