import requests
from django.conf import settings


class OAuth2Client:
    def __init__(self, provider, code, redirect_uri, state=None):
        self.provider = provider
        self.code = code
        self.redirect_uri = redirect_uri
        self.state = state

    def get_token_and_user_info(self):
        if self.provider == "kakao":
            return self._kakao()
        elif self.provider == "google":
            return self._google()
        elif self.provider == "naver":
            return self._naver()
        raise ValueError("Unsupported provider")

    def _kakao(self):
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": self.redirect_uri,
            "code": self.code,
        }
        access_token = requests.post(token_url, data=data).json().get("access_token")
        user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
        return access_token, {
            "provider_user_id": str(user_info["id"]),
            "email": user_info.get("kakao_account", {}).get("email"),
            "nickname": user_info.get("properties", {}).get("nickname"),
            "profile": user_info.get("properties", {}).get("profile_image"),
        }

    def _google(self):
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": self.redirect_uri,
            "code": self.code,
        }
        access_token = requests.post(token_url, data=data).json().get("access_token")
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()
        return access_token, {
            "provider_user_id": user_info["id"],
            "email": user_info.get("email"),
            "nickname": user_info.get("name"),
            "profile": user_info.get("picture"),
        }

    def _naver(self):
        token_url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": self.code,
            "state": self.state,
        }
        access_token = requests.post(token_url, data=data).json().get("access_token")
        user_info = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()["response"]
        return access_token, {
            "provider_user_id": user_info["id"],
            "email": user_info.get("email"),
            "nickname": user_info.get("nickname"),
            "profile": user_info.get("profile_image"),
        }
