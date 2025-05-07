from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .apis import OAuth2Client
from .models import SocialAccount, User
from .serializers import OAuthLoginSerializer, UserSerializer


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

        # 소셜 계정 존재 여부 확인 및 유저 생성
        social_account, created = SocialAccount.objects.get_or_create(
            provider=provider,
            provider_user_id=user_info["provider_user_id"],
            defaults={
                "user": User.objects.create(
                    username=f"{provider}_{user_info['provider_user_id']}",
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
