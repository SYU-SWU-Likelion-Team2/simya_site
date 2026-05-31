from django.urls import path

from .views import (
    DraftView,
    FeedListView,
    PostDeleteView,
    PostDetailView,
    PostPublishView,
)

app_name = "posts"

urlpatterns = [
    # 임시저장
    path("draft/",          DraftView.as_view(),       name="draft"),

    # 글 게시
    path("publish/",        PostPublishView.as_view(), name="publish"),

    # 피드
    path("feed/",           FeedListView.as_view(),    name="feed"),

    # 상세 조회
    path("<int:pk>/",       PostDetailView.as_view(),  name="detail"),

    # 삭제
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="delete"),
]