from django.urls import path
from . import views

app_name = 'mim'

urlpatterns = [
    path('', views.memes, name='memes'),
    path('upload/', views.upload_meme, name='upload_meme'),
    path('top_memes/', views.top_memes, name='top_memes'),
    path('trending/', views.trending_memes, name='trending'),
    path('meme_detail/<int:meme_id>/', views.meme_detail, name='meme_detail'),
    path('logout/', views.discord_logout, name='logout'),
    path('check-auth/', views.check_auth, name='check_auth'),
]