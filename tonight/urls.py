from django.urls import path
from . import views

app_name = 'tonight'

urlpatterns = [
    path('',                        views.index,    name='index'),
    path('write/',                  views.write,    name='write'),
    path('firewood/',               views.firewood, name='firewood'),
    path('detail/<int:post_id>/',   views.detail,   name='detail'),
    path('edit/<int:post_id>/',     views.edit,     name='edit'),
    path('comments/<int:post_id>/', views.comments, name='comments'),
    path('reaction/<int:post_id>/', views.reaction, name='reaction'),
    path('delete/<int:post_id>/', views.delete, name='delete'),
]