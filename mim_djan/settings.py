import os
from pathlib import Path

IS_LOCAL = os.environ.get('DJANGO_ENV', 'local') == 'local'

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure--nq$ryt)0qu)mvej=f@_vpjs8&-cw43x)x@rprl8kl4wz2gkty' if not IS_LOCAL else 'django-insecure--nq$ryt)0qu)mvej=f@_vpjs8&-cw43x)x@rprl8kl4wz2gkty'  # Згенеруй локальний ключ

DEBUG = IS_LOCAL

ALLOWED_HOSTS = ['fler432v.pythonanywhere.com'] if not IS_LOCAL else ['localhost', '127.0.0.1']

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

if IS_LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
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
SOCIAL_AUTH_DISCORD_EXTRA_DATA = [
    ('id', 'id'),
    ('username', 'username'),
    ('avatar', 'avatar'),
]

SOCIAL_AUTH_REDIRECT_URI = 'http://127.0.0.1:8000/complete/discord/' if IS_LOCAL else 'https://fler432v.pythonanywhere.com/complete/discord/'

SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_URL = '/login/discord/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles' if not IS_LOCAL else ''

MEDIA_URL = '/source/'
MEDIA_ROOT = BASE_DIR / 'source'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if IS_LOCAL:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }