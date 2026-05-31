from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['uuid', 'email', 'nickname', 'onboarding_step', 'created_at']
        read_only_fields = ['uuid', 'email', 'created_at']


class NicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['nickname']
        # nickname 외 필드는 이 serializer로 수정 불가
        read_only_fields = []

    def validate_nickname(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("닉네임을 입력해주세요.")
        if len(value) > 20:
            raise serializers.ValidationError("닉네임은 최대 20자입니다.")
        return value


class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['onboarding_step']

    def validate_onboarding_step(self, value: int) -> int:
        # 필요 시 최대 step 수를 여기서 제한
        MAX_STEP = 10
        if value < 0 or value > MAX_STEP:
            raise serializers.ValidationError(f"onboarding_step은 0~{MAX_STEP} 사이여야 합니다.")
        return value


class AnonymousUserSerializer(serializers.Serializer):
    """익명 유저 생성 요청 바디"""
    device_id = serializers.UUIDField()