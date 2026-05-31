from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View

from .serializers import (
    UserSerializer,
    NicknameSerializer,
    OnboardingSerializer,
    AnonymousUserSerializer,
)

User = get_user_model()


# ------------------------------------------------------------------ #
# 공통 헬퍼                                                             #
# ------------------------------------------------------------------ #

def get_jwt_token(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ------------------------------------------------------------------ #
# 기존 뷰 (수정 없이 유지)                                               #
# ------------------------------------------------------------------ #

class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': '인가 코드가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            if not user or not user.is_authenticated:
                return Response({'error': '구글 인증 유저를 찾을 수 없습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

            token = get_jwt_token(user)
            return Response({
                'token': token,
                'nickname': user.nickname,
                'is_new': not user.nickname,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """프로필 조회"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """닉네임 수정"""
        serializer = NicknameSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "닉네임이 성공적으로 변경되었습니다.",
                "user": serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------ #
# 신규: 익명 유저 생성 + JWT 발급                                         #
# ------------------------------------------------------------------ #

class AnonymousLoginView(APIView):
    """
    POST /accounts/anonymous/
    Body: { "device_id": "<UUID>" }

    device_id 로 유저를 찾거나 생성 후 JWT 발급.
    같은 device_id 로 재요청하면 항상 동일 유저의 토큰을 반환 (멱등).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AnonymousUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_id = str(serializer.validated_data['device_id'])
        user = User.objects.create_anonymous_user(device_id)

        return Response({
            'token': get_jwt_token(user),
            'is_new': not user.nickname,
            'onboarding_step': user.onboarding_step,
        }, status=status.HTTP_200_OK)


# ------------------------------------------------------------------ #
# 신규: 토큰 갱신                                                        #
# ------------------------------------------------------------------ #

class TokenRefreshView(APIView):
    """
    POST /accounts/token/refresh/
    Body: { "refresh": "<refresh_token>" }

    simplejwt 기본 뷰(TokenRefreshView)를 그대로 써도 되지만,
    응답 포맷을 프로젝트에 맞게 통일하려면 이 뷰를 사용.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'refresh 토큰이 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response(
                {'error': '유효하지 않거나 만료된 토큰입니다.', 'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# ------------------------------------------------------------------ #
# 신규: 온보딩 단계 저장 / 조회                                            #
# ------------------------------------------------------------------ #

class OnboardingView(APIView):
    """
    GET   /accounts/onboarding/  → 현재 단계 조회
    PATCH /accounts/onboarding/  → 단계 업데이트
    Body: { "onboarding_step": 2 }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'onboarding_step': request.user.onboarding_step})

    def patch(self, request):
        serializer = OnboardingSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': '온보딩 단계가 저장되었습니다.',
            'onboarding_step': serializer.data['onboarding_step'],
        }, status=status.HTTP_200_OK)

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        email = request.data.get('email', '')

        if not all([username, password, nickname]):
            return Response({'error': '아이디, 비밀번호, 닉네임은 필수입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': '이미 사용 중인 아이디입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if email and User.objects.filter(email=email).exists():
            return Response({'error': '이미 사용 중인 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email or f"{username}@simya.local", password=password, nickname=nickname)
        return Response({'token': get_jwt_token(user)}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'token': get_jwt_token(user)}, status=status.HTTP_200_OK)

class LoginPageView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('loginId')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/tonight/')
        return render(request, 'auth/login.html', {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})

class SignupPageView(View):
    def get(self, request):
        return render(request, 'auth/signup.html')