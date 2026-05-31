from django.urls import path
from .views import SignupPageView, LoginPageView

app_name = 'accounts'

urlpatterns = [
    path('login/',  LoginPageView.as_view(),  name='login'),
    path('signup/', SignupPageView.as_view(), name='signup'),
]