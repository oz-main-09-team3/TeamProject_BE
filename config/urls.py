from django.contrib import admin
from django.urls import path

from users.views import OAuthLoginAPI

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/social_login/", OAuthLoginAPI.as_view(), name="social_login"),

]
