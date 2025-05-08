import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "envs" / "dev.env")  # 루트의 dev.env 로드

DEBUG = True
ALLOWED_HOSTS = []


DATABASES["default"].update(
    {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),  # dev.env에 있는 DB 이름
        "USER": os.getenv("POSTGRES_USER"),  # dev.env에 있는 해당 DB 유저
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),  # dev.env에 있는 DB 패스워드
        "HOST": os.getenv("POSTGRES_HOST"),  # dev.env에 있는 DB HOST
        "PORT": os.getenv("POSTGRES_PORT"),  # dev.env에 있는 DB PORT
    }
)
