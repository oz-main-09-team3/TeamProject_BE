from django.contrib import admin

from apps.diary.models import Diary, DiaryImage

admin.site.register(DiaryImage)
admin.site.register(Diary)
