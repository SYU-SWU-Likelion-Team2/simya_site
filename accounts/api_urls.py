from django.urls import path
from . import views

urlpatterns = [
    path('signup/',        views.SignupView.as_view(),          name='api-signup'),
    path('login/',         views.LoginView.as_view(),           name='api-login'),
    path('profile/',       views.ProfileView.as_view(),         name='api-profile'),
    path('google/callback/', views.GoogleCallbackView.as_view(), name='api-google-callback'),
    path('anonymous/',     views.AnonymousLoginView.as_view(),  name='api-anonymous'),
    path('token/refresh/', views.TokenRefreshView.as_view(),    name='api-token-refresh'),
    path('onboarding/',    views.OnboardingView.as_view(),      name='api-onboarding'),
]