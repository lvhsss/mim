from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mim.urls')),  # Маршрути твого додатку
    path('', include('social_django.urls', namespace='social')),  # Маршрути для Discord OAuth
    path('accounts/', include('django.contrib.auth.urls')),  # Додаємо маршрути автентифікації Django
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)