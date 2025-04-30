import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SocialAccount

User = get_user_model()


def get_or_create_social_user(provider, access_token):
    # 소셜 API 요청
    profile = get_social_profile(provider, access_token)

    provider_user_id = profile["id"]
    nickname = profile.get("nickname", "user")

    # 유저 조회 또는 생성
    try:
        social_account = SocialAccount.objects.get(
            provider=provider, provider_user_id=provider_user_id
        )
        user = social_account.user
    except SocialAccount.DoesNotExist:
        user = User.objects.create_user(
            username=f"{provider}_{provider_user_id}",
            password=None,
            nickname=nickname,
        )
        SocialAccount.objects.create(
            user=user, provider=provider, provider_user_id=provider_user_id
        )

    # JWT 발급
    refresh = RefreshToken.for_user(user)
    return user, {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_id": user.id,
        "nickname": user.nickname,
    }


def get_social_profile(provider, access_token):
    if provider == "kakao":
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            raise ValueError("Invalid kakao token")
        profile = res.json()
        return {
            "id": profile["id"],
            "nickname": profile["properties"].get("nickname", "user"),
        }

    elif provider == "google":
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            raise ValueError("Invalid google token")
        profile = res.json()
        return {"id": profile["id"], "nickname": profile.get("name", "user")}

    elif provider == "naver":
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            raise ValueError("Invalid naver token")
        profile = res.json()["response"]
        return {"id": profile["id"], "nickname": profile.get("nickname", "user")}

    else:
        raise ValueError("Unsupported provider")
