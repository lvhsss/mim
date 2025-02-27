from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mim import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mim.urls', namespace='mim')),
    path('logout/', views.discord_logout, name='logout'),
    path('', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)