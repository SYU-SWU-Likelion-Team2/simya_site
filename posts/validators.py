from datetime import datetime, timezone as dt_timezone, timedelta

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Post

# 허용 게시 시간대: 06:00 ~ 23:00 (로컬 기준)
ALLOWED_START_HOUR = 6
ALLOWED_END_HOUR   = 23


def validate_posting_time(tz_offset_minutes: int) -> None:
    """
    유저의 로컬 시각이 허용 시간대(06:00~23:00)인지 검증한다.

    :param tz_offset_minutes: UTC+N 을 분 단위로 표현 (e.g. KST=540)
    :raises ValidationError: 허용 시간대 외 요청 시
    """
    user_tz   = dt_timezone(timedelta(minutes=tz_offset_minutes))
    local_now = datetime.now(tz=user_tz)

    if not (ALLOWED_START_HOUR <= local_now.hour < ALLOWED_END_HOUR):
        raise ValidationError(
            f"글은 {ALLOWED_START_HOUR:02d}:00 ~ {ALLOWED_END_HOUR:02d}:00 사이에만 게시할 수 있습니다."
        )


def validate_no_duplicate_today(user_id: int, tz_offset_minutes: int) -> None:
    """
    오늘(로컬 날짜 기준) 이미 게시한 글이 있으면 중복으로 간주해 차단한다.

    :param user_id: 작성자 PK
    :param tz_offset_minutes: UTC offset (분)
    :raises ValidationError: 오늘 이미 게시된 글이 존재할 때
    """
    user_tz   = dt_timezone(timedelta(minutes=tz_offset_minutes))
    local_now = datetime.now(tz=user_tz)

    # 오늘 00:00:00 / 내일 00:00:00 → UTC 변환
    today_start_local = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end_local   = today_start_local + timedelta(days=1)

    today_start_utc = today_start_local.astimezone(dt_timezone.utc)
    today_end_utc   = today_end_local.astimezone(dt_timezone.utc)

    exists = Post.objects.filter(
        author_id    = user_id,
        is_published = True,
        published_at__gte = today_start_utc,
        published_at__lt  = today_end_utc,
    ).exists()

    if exists:
        raise ValidationError("오늘은 이미 글을 게시했습니다. 하루에 한 번만 게시할 수 있습니다.")