from dotenv import dotenv_values

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["43.201.23.196"]
# dotenv_values("../envs/prod.env") 로 실제 DB/SECRET_KEY 읽어오기


# dotenv_values : env 파일의 경로를 파라미터로 전달 받아 해당 파일을 읽어온 후 key, value 형태로 매핑하여 dict로 반환한다.
ENV = dotenv_values("../envs/prod.env")