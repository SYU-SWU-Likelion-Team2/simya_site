import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('아이디는 필수 항목입니다.')
        user = self.model(username=username, email=email or '', **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username=username, email=email, password=password, **extra_fields)

    # ------------------------------------------------------------------ #
    # 익명 유저 생성                                                         #
    # ------------------------------------------------------------------ #
    def create_anonymous_user(self, device_id: str) -> "User":
        """
        device_id 기반 익명 유저 생성 (없으면 생성, 있으면 조회).
        - email: anon_<device_id>@anonymous.local (unique 보장)
        - is_anonymous: True
        """
        email = f"anon_{device_id}@anonymous.local"
        user, _ = self.get_or_create(
            email=email,
            defaults={
                "is_anonymous_user": True,
                "nickname": "",
            },
        )
        if not user.has_usable_password():
            user.set_unusable_password()
            user.save(update_fields=["password"])
        return user


class User(AbstractBaseUser, PermissionsMixin):
    uuid       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email      = models.EmailField(unique=True)
    username   = models.CharField(max_length=30, unique=True, default='')
    nickname   = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_anonymous_user = models.BooleanField(default=False)
    onboarding_step = models.PositiveSmallIntegerField(default=0)

    is_staff  = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'  # email → username 변경
    REQUIRED_FIELDS = ['email']  # 추가

    def __str__(self):
        return f"{'[anon] ' if self.is_anonymous_user else ''}{self.username}"