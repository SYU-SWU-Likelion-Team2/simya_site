from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.api_urls')),        # API용
    path('accounts/', include('accounts.urls', namespace='accounts')),  # 페이지용
    path('accounts/', include('allauth.urls')),
    path('tonight/', include('tonight.urls', namespace='tonight')),
    path('posts/', include('posts.urls', namespace='posts')),
]