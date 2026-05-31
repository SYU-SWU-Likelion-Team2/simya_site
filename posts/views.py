from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Draft, Post
from .serializers import (
    DraftSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    PostFeedSerializer,
)
from .validators import validate_no_duplicate_today, validate_posting_time


# ------------------------------------------------------------------ #
# 임시저장                                                              #
# ------------------------------------------------------------------ #

class DraftView(APIView):
    """
    GET  /posts/draft/   → 임시저장 불러오기
    PUT  /posts/draft/   → 임시저장 저장 (upsert)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        draft, _ = Draft.objects.get_or_create(author=request.user)
        return Response(DraftSerializer(draft).data)

    def put(self, request: Request) -> Response:
        draft, _ = Draft.objects.get_or_create(author=request.user)
        serializer = DraftSerializer(draft, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ------------------------------------------------------------------ #
# 글 게시                                                               #
# ------------------------------------------------------------------ #

class PostPublishView(APIView):
    """
    POST /posts/publish/
    - 시간대 검증
    - 오늘 중복 검증
    - 게시 + 만료 시각 계산
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tz_offset = serializer.validated_data.get("timezone_offset", 0)

        # 규칙 검증
        validate_posting_time(tz_offset)
        validate_no_duplicate_today(request.user.pk, tz_offset)

        # 저장 후 게시
        post = serializer.save(author=request.user)
        post.publish()

        return Response(
            PostDetailSerializer(post).data,
            status=status.HTTP_201_CREATED,
        )


# ------------------------------------------------------------------ #
# 피드 (타인 글 목록)                                                    #
# ------------------------------------------------------------------ #

class FeedListView(generics.ListAPIView):
    """
    GET /posts/feed/?page=1
    - 만료되지 않은 타인의 게시글 최신순
    - cursor 기반 페이지네이션은 settings.py 에서 DEFAULT_PAGINATION_CLASS 로 설정
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = PostFeedSerializer

    def get_queryset(self):
        now = timezone.now()
        return (
            Post.objects.filter(
                is_published = True,
                expires_at__gt = now,       # 만료 전 글만
            )
            .exclude(author=self.request.user)  # 본인 글 제외
            .select_related("author")
            .order_by("-created_at")
        )


# ------------------------------------------------------------------ #
# 글 상세 조회                                                           #
# ------------------------------------------------------------------ #

class PostDetailView(APIView):
    """GET /posts/<pk>/"""
    permission_classes = [permissions.IsAuthenticated]

    def _get_post(self, pk: int) -> Post:
        try:
            return Post.objects.select_related("author").get(
                pk=pk,
                is_published=True,
            )
        except Post.DoesNotExist:
            raise NotFound("게시글을 찾을 수 없습니다.")

    def get(self, request: Request, pk: int) -> Response:
        post = self._get_post(pk)

        if post.is_expired:
            raise NotFound("이미 만료된 게시글입니다.")

        return Response(PostDetailSerializer(post).data)


# ------------------------------------------------------------------ #
# 글 삭제 (본인만)                                                       #
# ------------------------------------------------------------------ #

class PostDeleteView(APIView):
    """DELETE /posts/<pk>/delete/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request: Request, pk: int) -> Response:
        try:
            post = Post.objects.get(pk=pk, is_published=True)
        except Post.DoesNotExist:
            raise NotFound("게시글을 찾을 수 없습니다.")

        if post.author_id != request.user.pk:
            raise PermissionDenied("본인의 글만 삭제할 수 있습니다.")

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)