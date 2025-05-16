import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "envs" / "prod.env")  # 루트의 .env 로드

DEBUG = False
ALLOWED_HOSTS = ["handsomepotato.p-e.kr", "43.201.23.196"]


DATABASES["default"].update(
    {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),  # prod.env에 있는 DB 이름
        "USER": os.getenv("POSTGRES_USER"),  # prod.env에 있는 해당 DB 유저
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),  # prod.env에 있는 DB 패스워드
        "HOST": os.getenv("POSTGRES_HOST"),  # prod.env에 있는 DB HOST
        "PORT": os.getenv("POSTGRES_PORT"),  # prod.env에 있는 DB PORT
    }
)

AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_ACL = "public-read"

LOGGING = DEFAULT_LOGGING
