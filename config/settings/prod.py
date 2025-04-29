from .base import *


DEBUG = False
ALLOWED_HOSTS = ['54.180.95.137', 'ec2-54-180-95-137.ap-northeast-2.compute.amazonaws.com']
# dotenv_values("../envs/prod.env") 로 실제 DB/SECRET_KEY 읽어오기


# dotenv_values : env 파일의 경로를 파라미터로 전달 받아 해당 파일을 읽어온 후 key, value 형태로 매핑하여 dict로 반환한다.
ENV = dotenv_values("../envs/prod.env")