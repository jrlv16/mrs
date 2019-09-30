"""
Django settings for mrs project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

from crudlfap.settings import (
    CRUDLFAP_APPS,
    CRUDLFAP_TEMPLATE_BACKEND,
    DJANGO_APPS,
)

import git
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.transport import HttpTransport

from mrs.context_processors import strip_password

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        '..',
    )
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'notsecret')

DEBUG = os.getenv('DEBUG', False)

if not DEBUG and 'SECRET_KEY' not in os.environ:
    raise Exception('$SECRET_KEY is required if DEBUG is False')

ALLOWED_HOSTS = []
if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

if 'HOST' in os.environ and os.getenv('HOST') not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(os.getenv('HOST'))

if not DEBUG and 'ALLOWED_HOSTS' not in os.environ:
    raise Exception('$ALLOWED_HOSTS is required if DEBUG is False')

LOGIN_REDIRECT_URL = '/admin/'

CRUDLFAP_APPS.pop(CRUDLFAP_APPS.index('crudlfap_auth'))
INSTALLED_APPS = [
    'contact',
    'institution',
    'person',
    'mrs',
    'mrsrequest', 'jfu',
    'mrsattachment',
    'mrsemail',
    'mrsstat',
    'caisse',
    'rating',
    'pro',
    'denorm',
    'explorer',
    'captcha',

    os.getenv('WEBPACK_LOADER', 'webpack_loader'),
    'django_humanize',
] + CRUDLFAP_APPS + DJANGO_APPS + [
    'djcall',
    'crudlfap_auth', 'mrsuser',  # the second overrides the first
    'django.contrib.admindocs',
]

AUTH_USER_MODEL = 'mrsuser.User'

if not os.getenv('CI'):
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'threadlocals.middleware.ThreadLocalMiddleware',
    'mrs.middleware.BasicAuthMiddleware',
]

ROOT_URLCONF = 'mrs.urls'

CRUDLFAP_TEMPLATE_BACKEND['OPTIONS']['globals'].setdefault(
    'naturalsize', 'humanize.naturalsize')
CRUDLFAP_TEMPLATE_BACKEND['OPTIONS']['globals'].setdefault(
    'localtime', 'django.utils.timezone.template_localtime')
CRUDLFAP_TEMPLATE_BACKEND['OPTIONS']['globals'].setdefault('list', list)
CRUDLFAP_TEMPLATE_BACKEND['OPTIONS']['globals'].setdefault('float', float)

if os.getenv('WEBPACK_LOADER') == 'webpack_mock':
    CRUDLFAP_TEMPLATE_BACKEND['OPTIONS']['globals']['render_bundle'] = (
        'webpack_mock.templatetags.webpack_loader.render_bundle')

TEMPLATES = [
    CRUDLFAP_TEMPLATE_BACKEND,
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "contact.context_processors.contact_form",
                "mrs.context_processors.settings",
                "mrs.context_processors.header_links",
            ],
        },
    },
]

WSGI_APPLICATION = 'mrs.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('DB_USER', None),
        'PASSWORD': os.getenv('DB_PASSWORD', None),
        'HOST': os.getenv(
            'DB_HOST',
            os.getenv('POSTGRES_PORT_5432_TCP_ADDR', None)
        ),
        'PORT': os.getenv('DB_PORT', None),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.{}'.format(n),
    } for n in [
        'UserAttributeSimilarityValidator',
        'MinimumLengthValidator',
        'CommonPasswordValidator',
        'NumericPasswordValidator',
    ]
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'mrsrequest.backends.AuthenticationBackend',
    'crudlfap_auth.backends.ViewBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/


LOCALE = 'fr_FR'
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = os.environ.get('TIME_ZONE', 'Europe/Paris')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = os.getenv('STATIC_URL', '/static/')
if not STATIC_URL.endswith('/'):
    STATIC_URL += '/'
STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'collected'))

DEFAULT_FILE_STORAGE = 'db_file_storage.storage.DatabaseFileStorage'

EMAIL_HOST = os.getenv('EMAIL_HOST', None)
EMAIL_PORT = os.getenv('EMAIL_PORT', None)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', None)
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', None)
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', None)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'from@example.com')
TEAM_EMAIL = os.getenv('TEAM_EMAIL', 'team@example.com')
LIQUIDATION_EMAIL = os.getenv('LIQUIDATION_EMAIL', 'liquidation@example.com')

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', EMAIL_BACKEND)

PREFIX = os.getenv('PLAYLABS_PREFIX', 'mrs')
INSTANCE = os.getenv('PLAYLABS_INSTANCE', 'dev')

COLORS = {
    'DEV': 'tomato',
    'STAGING': 'SandyBrown',
    'ECOLE': 'aquamarine',
    'JPIC': 'gold',  # j -> jaune, bichon -> or
    'VINDAREL': 'BlueViolet',
    'TBINETRUY': 'PaleTurquoise',
}

# Visually differentiate the environments from prod:
# with a colored breadcrumb...
CRUDLFAP_TEMPLATE_BACKEND['OPTIONS']['constants'].update(dict(
    BACKGROUND_COLOR=COLORS.get(INSTANCE.upper(), ''),
))

# and the page's title.
TITLE_SUFFIX = ""
if INSTANCE.upper() != 'PRODUCTION':
    TITLE_SUFFIX = " ({})".format(INSTANCE.upper())

# Intégration de Sentry-sdk
# https://docs.sentry.io/platforms/python/django/

# Paramètres
SENTRY_DSN = os.getenv('SENTRY_DSN', '')

# Récupération du hash de la release courante
RELEASE = os.getenv('GIT_COMMIT', '')
if not RELEASE:
    repo = os.path.join(os.path.dirname(__file__), '..', '..')
    if os.path.exists(os.path.join(repo, '.git')):
        repo = git.Repo(search_parent_directories=False)
        RELEASE = repo.head.object.hexsha

# Initialisation de Sentry côté Django
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    release=RELEASE,
    environment=INSTANCE,
    transport=HttpTransport
)

# Paramètres Sentry publics pour les erreurs côté Front,
# intégrés dans le context_processor
SENTRY_PUBLIC_CONFIG = dict(
    environment=INSTANCE,
    release=RELEASE,
)

# Retrait du secret
SENTRY_PUBLIC_DSN = strip_password(SENTRY_DSN)

# Paramètres Sentry publics pour les erreurs côté Front / Crudlfap
CRUDLFAP_TEMPLATE_BACKEND['OPTIONS']['constants'].update(dict(
    SENTRY_DSN=SENTRY_PUBLIC_DSN,
    SENTRY_CONFIG=SENTRY_PUBLIC_CONFIG,
))

BASE_URL = 'http://localhost:8000'
if 'HOST' in os.environ:
    SITE_DOMAIN = os.getenv('HOST')
    BASE_URL = 'https://{}'.format(SITE_DOMAIN)


def is_admin(user):
    return user.is_authenticated and user.profile == 'admin'


EXPLORER_CONNECTIONS = {
    'Default': 'default'
}
EXPLORER_DEFAULT_CONNECTION = 'default'
EXPLORER_PERMISSION_VIEW = EXPLORER_PERMISSION_CHANGE = is_admin


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
if os.getenv('LOG'):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'file.error': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': os.path.join(
                    os.getenv('LOG'),
                    'django.error.log',
                ),
                'formatter': 'simple',
            },
            'file.info': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': os.path.join(
                    os.getenv('LOG'),
                    'django.info.log',
                ),
                'formatter': 'simple'
            },
            'file.debug': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': os.path.join(
                    os.getenv('LOG'),
                    'django.debug.log',
                ),
                'formatter': 'simple'
            },
            'file.djcall': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': os.path.join(
                    os.getenv('LOG'),
                    'djcall.log',
                ),
            },
            'file.sql': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': os.path.join(
                    os.getenv('LOG'),
                    'django.sql.log',
                ),
                'formatter': 'simple'
            },
            'file.request': {
                'level': LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': os.path.join(
                    os.getenv('LOG'),
                    'django.request.log',
                ),
                'formatter': 'simple'
            },
        },
        'formatters': {
            'simple': {
                'format': '%(levelname)s [%(name)s] %(message)s'
            },
        },
        'loggers': {
            'django.request': {
                'handlers': [
                    'file.request',
                ],
                'level': LOG_LEVEL,
                'propagate': True,
            },
            'django.db': {
                'handlers': [
                    'file.sql',
                ],
                'level': LOG_LEVEL,
                'propagate': True,
            },
            'djcall': {
                'handlers': [
                    'file.djcall',
                    'console'
                ],
                'level': LOG_LEVEL,
                'propagate': True,
            },
        },
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'formatters': {
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'loggers': {
            # 'django.db': {
            #     'handlers': ['console'],
            #     'level': 'DEBUG',
            #     'propagate': True,
            # },
            '*': {
                'handlers': ['console'],
                'level': LOG_LEVEL,
                'propagate': True,
            },
        },
    }
    if not os.getenv('CI'):
        LOGGING['loggers']['djcall'] = {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        }

if DEBUG:
    try:
        import dbdiff  # noqa
    except ImportError:
        pass
    else:
        INSTALLED_APPS += ('dbdiff',)

    try:
        import debug_toolbar  # noqa
    except ImportError:
        pass
    else:
        INSTALLED_APPS += ('debug_toolbar',)
        MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
        INTERNAL_IPS = ['172.17.0.1', '127.0.0.1']


DATE_FORMAT_FR = '%d/%m/%Y'

CAPTCHA_IMAGE_SIZE = (188, 60)
CAPTCHA_FONT_SIZE = 32
CAPTCHA_LENGTH = 6
CAPTCHA_NOISE_FUNCTIONS = (
    'contact.captcha.noise_arcs',
    'contact.captcha.noise_dots',
)
CAPTCHA_FOREGROUND_COLOR = '#507886'
CAPTCHA_LETTER_ROTATION = (-35, 35)

'''
# works, but lacks french support for now, see
# https://github.com/betagouv/mrs/issues/971#issuecomment-476777116
if os.path.exists('/usr/bin/flite'):
    CAPTCHA_FLITE_PATH = '/usr/bin/flite'
    CAPTCHA_SOX_PATH = '/usr/bin/sox'
'''
