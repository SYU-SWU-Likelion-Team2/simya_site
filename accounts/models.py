from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    #기본 필드
    nickname = models.CharField(max_length=50, blank=True, verbose_name="닉네임")

    class Meta:
        db_table = 'user'