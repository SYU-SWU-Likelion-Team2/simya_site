from django.utils import timezone
from rest_framework import serializers

from .models import Draft, FirewoodType, Post


# ------------------------------------------------------------------ #
# Draft                                                                #
# ------------------------------------------------------------------ #

class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Draft
        fields = ["content", "saved_at"]
        read_only_fields = ["saved_at"]


# ------------------------------------------------------------------ #
# Post - 게시용                                                         #
# ------------------------------------------------------------------ #

class PostCreateSerializer(serializers.ModelSerializer):
    """글 게시 요청 바디"""
    class Meta:
        model  = Post
        fields = ["content", "firewood_type", "timezone_offset"]

    def validate_firewood_type(self, value: str) -> str:
        if value not in FirewoodType.values:
            raise serializers.ValidationError(
                f"firewood_type은 {FirewoodType.values} 중 하나여야 합니다."
            )
        return value

    def validate_content(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("내용을 입력해주세요.")
        if len(value) > 2000:
            raise serializers.ValidationError("최대 2000자까지 입력할 수 있습니다.")
        return value


class PostFeedSerializer(serializers.ModelSerializer):
    """피드 목록 - 최소 정보"""
    is_expired = serializers.BooleanField(read_only=True)
    remaining_seconds = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            "id",
            "content",
            "firewood_type",
            "published_at",
            "expires_at",
            "is_expired",
            "remaining_seconds",
        ]

    def get_remaining_seconds(self, obj: Post) -> int | None:
        if obj.expires_at is None:
            return None
        delta = obj.expires_at - timezone.now()
        return max(int(delta.total_seconds()), 0)


class PostDetailSerializer(PostFeedSerializer):
    """글 상세 - 작성자 id 포함"""
    class Meta(PostFeedSerializer.Meta):
        fields = PostFeedSerializer.Meta.fields + ["author"]