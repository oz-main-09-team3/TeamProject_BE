"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

# 어떤 환경을 쓸지 결정 (기본: dev)
env_mode = os.getenv(
    "ENV_MODE", "dev"
)  # ENV_MODE는 system 환경변수로 넘기거나 .env에 명시
env_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "envs", f"{env_mode}.env"
)
load_dotenv(dotenv_path=env_path)

# DJANGO_SETTINGS_MODULE 자동 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = get_asgi_application()
