"""
Django settings for markinghell project.
Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import dj_database_url

ADMINS = MANAGERS = [] # TODO: Add your contact tuple ("John", "john@example.com") to receive error notifications
SITE_URL = 'https://localhost:8000' # TODO: Change this to your domain

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

LOGGING_DIR = os.path.join(PROJECT_DIR, 'log')
LOGGING_FILE = os.path.join(LOGGING_DIR, 'logfile.log')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure' # TODO: Change this to a random string

STRIPE_PUBLISH = os.environ.get('STRIPE_PUBLIC')
STRIPE_SECRET = os.environ.get('STRIPE_SECRET')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
DEPLOY_CONTEXT = os.environ.get('DEPLOY_CONTEXT', 'app')
LOGGER_NAME = DEPLOY_CONTEXT
BACKEND_DOMAIN = os.environ.get('BACKEND_DOMAIN', 'http://127.0.0.1:8091')
PAYMENT_SUCCESS_URL = f'{BACKEND_DOMAIN}/store/success/'
PAYMENT_CANCEL_URL = f'{BACKEND_DOMAIN}/store/cancel/'

# DEBUG = True if (os.environ.get('DEBUG', '0') == '1') else False # Original
DEBUG = True

try:
    from local_settings import *
except ImportError:
    pass

RQ_SHOW_ADMIN_LINK = True


if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    ########## EMAIL CONFIGURATION
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sparkpostmail.com'
    EMAIL_HOST_PASSWORD = ''
    EMAIL_HOST_USER = 'SMTP_Injection'
    EMAIL_SUBJECT_PREFIX = '[Workshop]'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    # SERVER_EMAIL = EMAIL_HOST_USER
    DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'no-reply@mail.domain.com' # TODO: Change this to your verified sending domain
    ########## END EMAIL CONFIGURATION

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1'] # TODO: Add your domain here
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Vite App Dir: point it to the folder your vite app is in.
VITE_APP_DIR = os.path.join(BASE_DIR, 'app', 'static')
DJANGO_VITE_ASSETS_PATH = '/static/dist/assets/'
DJANGO_VITE_STATIC_URL_PREFIX = 'dist'
DJANGO_VITE_DEV_MODE = DEBUG
DJANGO_VITE_DEV_SERVER_PORT = 3000
DJANGO_VITE_MANIFEST_PATH = os.path.join(VITE_APP_DIR, 'dist', 'manifest.json')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.messages',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'store',
    'django_rq',
    'django_vite',
    'studio_suite',
    'member_suite',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

DEFAULT_HOST = 'default'
ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'app', 'templates')],
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

WSGI_APPLICATION = 'app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

SQLITE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(default=f'sqlite:///{SQLITE_PATH}',
                                      conn_max_age=600,
                                      conn_health_checks=True)
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


### ALLAUTH SOCIAL ACCOUNTS ###
SOCIALACCOUNT_PROVIDERS = {
    # 'facebook': {
    #     'METHOD': 'oauth2',
    #     'SCOPE': ['email', 'public_profile', 'user_friends'],
    #     'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
    #     'INIT_PARAMS': {'cookie': True},
    #     'FIELDS': [
    #         'id',
    #         'email',
    #         'name',
    #         'first_name',
    #         'last_name',
    #         'verified',
    #         'locale',
    #         'timezone',
    #         'link',
    #         'gender',
    #         'updated_time',
    #     ],
    #     'EXCHANGE_TOKEN': True,
    #     'LOCALE_FUNC': 'path.to.callable',
    #     'VERIFIED_EMAIL': False,
    #     'VERSION': 'v2.12',
    # },
    # 'google': {
    #     'APP': {
    #         'client_id': '',
    #         'secret': '',
    #         'creation_date': '',
    #         'key': ''
    #     },
    #     'SCOPE': [
    #         'email',
    #     ],
    #     'AUTH_PARAMS': {
    #         'access_type': 'online',
    #     }
    # }
}

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/email/'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400  # 1 day in seconds
ACCOUNT_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_LOGOUT_ON_GET= True
ACCOUNT_UNIQUE_EMAIL = True

SOCIALACCOUNT_EMAIL_REQUIRED = ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_STORE_TOKENS=False
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
### END ALLAUTH SOCIAL ACCOUNTS ###


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
else:
    INTERNAL_IPS = []

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app', 'static')
]

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        #'LOCATION': 'redis://redis:6379'
        'LOCATION': 'redis://localhost:6379/1',  # Localhosting Redis Server
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

RQ_QUEUES = {
    # 'default': {
    #     'USE_REDIS_CACHE': 'default',
    # },
    'default': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'USERNAME': '',
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
        'REDIS_CLIENT_KWARGS': {},
    },
    # 'with-sentinel': {
    #     'SENTINELS': [('localhost', 26736), ('localhost', 26737)],
    #     'MASTER_NAME': 'redismaster',
    #     'DB': 0,
    #     # Redis username/password
    #     'USERNAME': 'redis-user',
    #     'PASSWORD': 'secret',
    #     'SOCKET_TIMEOUT': 0.3,
    #     'CONNECTION_KWARGS': {  # Eventual additional Redis connection arguments
    #         'ssl': True
    #     },
    #     'SENTINEL_KWARGS': {    # Eventual Sentinel connection arguments
    #         # If Sentinel also has auth, username/password can be passed here
    #         'username': 'sentinel-user',
    #         'password': 'secret',
    #     },
    # },
    # 'high': {
    #     'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379/0'), # If you're on Heroku
    #     'DEFAULT_TIMEOUT': 500,
    # },
    # 'low': {
    #     'HOST': 'localhost',
    #     'PORT': 6379,
    #     'DB': 0,
    # }
}

# RQ_EXCEPTION_HANDLERS = ['path.to.my.handler'] # If you need custom exception handlers
from django.utils.log import DEFAULT_LOGGING

LOG_FILTERS = {
    "require_debug_false": {
        "()": "django.utils.log.RequireDebugFalse",
    },
    "require_debug_true": {
        "()": "django.utils.log.RequireDebugTrue",
    },
},

LOG_FORMATTERS = {
    "rq_console": {
        "format": "%(asctime)s %(message)s",
        "datefmt": "%H:%M:%S",
    },
    "verbose": {
        "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
        "style": "{",
    },
    "simple": {
        "format": "{levelname} {message}",
        "style": "{",
    },
    "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
}

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": LOG_FORMATTERS,
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "rq_console": {
                "level": "DEBUG",
                "class": "rq.logutils.ColorizingStreamHandler",
                "formatter": "rq_console",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "worker": {
                "handlers": ["console"],
                "level": "INFO"
            },
            "app": {
                "handlers": ["console"],
                "level": "INFO"
            },
            "rq.worker": {
                "handlers": ["console"],
                "level": "INFO"
            },
            "django": {
                "handlers": ["console"],
                "level": "INFO",
            },
        }
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": LOG_FORMATTERS,
        "root": {
            "handlers": ["app_file", "mail_admins"],
            "level": "INFO",
        },
        "handlers": {
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
            "rq_file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": os.path.join(LOGGING_DIR, 'rq.log'),
                "formatter": "rq_console",
            },
            "app_file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": os.path.join(LOGGING_DIR, 'app.log'),
                "formatter": "verbose",
            }
        },
        "loggers": {
            "rq.worker": {
                "handlers": ["rq_file", "mail_admins"],
                "level": "INFO"
            },
            "django": {
                "handlers": ["app_file", "mail_admins"],
                "level": "INFO",
            },
            "worker": {
                "handlers": ["rq_file", "mail_admins"],
                "level": "INFO"
            },
            "app": {
                "handlers": ["app_file", "mail_admins"],
                "level": "INFO"
            },
        }
    }

try:
    from config import *
except ImportError:
    pass

