from .base import *

DEBUG = True
ALLOWED_HOSTS = []

# dotenv_values : env 파일의 경로를 파라미터로 전달 받아 해당 파일을 읽어온 후 key, value 형태로 매핑하여 dict로 반환한다.
ENV = dotenv_values("../envs/dev.env")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": ENV.get("POSTGRES_DB"),  # dev.env에 있는 DB 이름
        "USER": ENV.get("POSTGRES_USER"),  # dev.env에 있는 해당 DB 유저
        "PASSWORD": ENV.get("POSTGRES_PASSWORD"),  # dev.env에 있는 DB 패스워드
        "HOST": ENV.get("POSTGRES_HOST"),  # dev.env에 있는 DB HOST
        "PORT": ENV.get("POSTGRES_PORT"),  # dev.env에 있는 DB PORT
    }
}
