import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure--nq$ryt)0qu)mvej=f@_vpjs8&-cw43x)x@rprl8kl4wz2gkty'
DEBUG = True
ALLOWED_HOSTS = ['fler432v.pythonanywhere.com', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mim',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mim_djan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mim_djan.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fler432v$mim_db',
        'USER': 'fler432v',
        'PASSWORD': '1233955995Rtfgg@',
        'HOST': 'fler432v.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.discord.DiscordOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_DISCORD_KEY = '1342972978266243158'
SOCIAL_AUTH_DISCORD_SECRET = 'DmU8TacN5R5PVwyEFmheqODSJG1IaBHr'
SOCIAL_AUTH_DISCORD_SCOPE = ['identify']
SOCIAL_AUTH_REDIRECT_URI = 'http://fler432v.pythonanywhere.com/complete/discord/'
SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/source/'
MEDIA_ROOT = BASE_DIR / 'source'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'