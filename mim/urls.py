from django.urls import path
from . import views

app_name = 'mim'

urlpatterns = [
    path('', views.memes, name='memes'),
    path('top/', views.top_memes, name='top_memes'),
    path('trending/', views.trending_memes, name='trending'),
    path('upload/', views.upload_meme, name='upload_meme'),
    path('<int:meme_id>/', views.meme_detail, name='meme_detail'),
]