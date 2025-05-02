from .base import *
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env") # 루트의 .env 로드

DEBUG = False
ALLOWED_HOSTS = ["43.201.23.196"]


DATABASES["default"].update({
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),  # prod.env에 있는 DB 이름
        "USER": os.getenv("POSTGRES_USER"),  # prod.env에 있는 해당 DB 유저
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),  # prod.env에 있는 DB 패스워드
        "HOST": os.getenv("POSTGRES_HOST"),  # prod.env에 있는 DB HOST
        "PORT": os.getenv("POSTGRES_PORT"),  # prod.env에 있는 DB PORT
})

