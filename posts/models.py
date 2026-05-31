from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class FirewoodType(models.TextChoices):
    """장작 옵션 - 글 만료 시간 결정"""
    KINDLING = "kindling", "불쏘시개 (1시간)"   # 1h
    FIREWOOD  = "firewood",  "장작 (6시간)"      # 6h
    LOG       = "log",       "통나무 (24시간)"    # 24h


FIREWOOD_DURATION: dict[str, timedelta] = {
    FirewoodType.KINDLING: timedelta(hours=1),
    FirewoodType.FIREWOOD:  timedelta(hours=6),
    FirewoodType.LOG:       timedelta(hours=24),
}


class Post(models.Model):
    author       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    content      = models.TextField()
    firewood_type = models.CharField(
        max_length=10,
        choices=FirewoodType.choices,
        default=FirewoodType.FIREWOOD,
    )

    # 시간대 (HH:MM 형식, 허용 게시 시간대 저장)
    timezone_offset = models.SmallIntegerField(
        default=0,
        help_text="UTC 기준 offset (분 단위, e.g. +09:00 → 540)",
    )

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at   = models.DateTimeField(null=True, blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "is_published"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Post({self.pk}) by {self.author_id} [{self.firewood_type}]"

    # ------------------------------------------------------------------ #
    # 비즈니스 로직                                                         #
    # ------------------------------------------------------------------ #
    def publish(self) -> None:
        """글을 게시 상태로 전환하고 만료 시각을 계산한다."""
        now = timezone.now()
        self.is_published = True
        self.published_at = now
        self.expires_at   = now + FIREWOOD_DURATION[self.firewood_type]
        self.save(update_fields=["is_published", "published_at", "expires_at", "updated_at"])

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at


class Draft(models.Model):
    """임시저장 - 유저당 1개 (upsert 방식)"""
    author    = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="draft",
    )
    content   = models.TextField(blank=True, default="")
    saved_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft of {self.author_id}"

class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment({self.pk}) on Post({self.post_id})"


class Reaction(models.Model):
    class ReactionType(models.TextChoices):
        FIRE = 'fire', '불씨'
        STAY = 'stay', '곁에 머물기'

    post          = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    author        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=ReactionType.choices)

    class Meta:
        unique_together = ['post', 'author', 'reaction_type']

    def __str__(self):
        return f"Reaction({self.reaction_type}) on Post({self.post_id})"