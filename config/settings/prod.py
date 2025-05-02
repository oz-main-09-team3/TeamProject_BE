from .base import *

DEBUG = False
ALLOWED_HOSTS = ["43.201.23.196"]
# dotenv_values("../envs/prod.env") 로 실제 DB/SECRET_KEY 읽어오기


# dotenv_values : env 파일의 경로를 파라미터로 전달 받아 해당 파일을 읽어온 후 key, value 형태로 매핑하여 dict로 반환한다.
ENV = dotenv_values("../envs/prod.env")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": ENV.get("POSTGRES_DB"),  # prod.env에 있는 DB 이름
        "USER": ENV.get("POSTGRES_USER"),  # prod.env에 있는 해당 DB 유저
        "PASSWORD": ENV.get("POSTGRES_PASSWORD"),  # prod.env에 있는 DB 패스워드
        "HOST": ENV.get("POSTGRES_HOST"),  # prod.env에 있는 DB HOST
        "PORT": ENV.get("POSTGRES_PORT"),  # prod.env에 있는 DB PORT
    }
}