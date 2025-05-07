from django.contrib import admin
from django.urls import path, include

from apps import diary

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/diary/', include('apps.diary.urls')),
]
