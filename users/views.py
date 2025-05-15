import requests
from django.core.files.base import ContentFile
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import SocialAccount, User

from .apis import OAuth2Client
from .serializers import OAuthLoginSerializer, UserMeSerializer, UserSerializer


class OAuthLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    # 클라이언트가 보낸 code 를 검증
    def post(self, request, provider):
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        redirect_uri = request.data.get("redirect_uri")

        # OAuth2Client 를 통해 카카오 토큰과 사용자 정보 가져오기
        try:
            oauth_client = OAuth2Client(provider, code, redirect_uri)
            access_token, user_info = oauth_client.get_token_and_user_info()

            # provider_user_id 와 username 구성
            provider_user_id = str(user_info["id"])
            username = f"{provider}{provider_user_id}"

            # 이미 연결된 SocialAccount 가 있는지 확인
            try:
                social_account = SocialAccount.objects.get(
                    provider=provider, provider_user_id=provider_user_id
                )
                user = social_account.user

                # ↪ 기존 유저라면 user_info로 매번 업데이트
                updated = False
                update_fields = []
                for field, new_val in {
                    "nickname": user_info.get("nickname"),
                    "phone_num": user_info.get("phone_number"),
                    "birthday": user_info.get("birthday"),
                    "email": user_info.get("email"),
                }.items():
                    if new_val and getattr(user, field) != new_val:
                        setattr(user, field, new_val)
                        updated = True
                        update_fields.append(field)
                if updated:
                    user.save(update_fields=update_fields)

            except SocialAccount.DoesNotExist:
                # 새 소셜로그인인 경우 User 생성 또는 조회
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "nickname": user_info.get("nickname", ""),
                        "phone_num": user_info.get("phone_number", ""),
                        "birthday": user_info.get("birthday", ""),
                        "email": user_info.get("email", ""),
                    },
                )
                # SocialAccount 연결
                SocialAccount.objects.create(
                    provider=provider, provider_user_id=provider_user_id, user=user
                )

            # 프로필 이미지 다운로드 후 S3(또는 로컬)에 저장
            profile_url = user_info.get("profile_img")
            if profile_url:
                try:
                    response = requests.get(profile_url, timeout=5)
                    response.raise_for_status()
                    filename = f"{provider}_{provider_user_id}.jpg"
                    user.profile.save(
                        filename, ContentFile(response.content), save=True
                    )
                except Exception as e:
                    print(f"⚠️ 프로필 이미지 저장 실패: {e}", flush=True)
            # JWT 토큰 발급
            refresh = RefreshToken.for_user(user)

            # 최종 응답
            return Response(
                {
                    "token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": UserSerializer(user).data,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)


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
