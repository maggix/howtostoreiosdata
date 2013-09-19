from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_DIR.child('db.sqlite3'),
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_PORT = 2525
SECRET_KEY = 'i=s)9x^(s(w$f=7!a-8&n5b1ps^zbdl#!rxq+s@oqqr=pr4_5h'

INTERNAL_IPS = ('127.0.0.1',)

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )

INSTALLED_APPS += (
    'debug_toolbar',
)

TEST_RUNNER = 'discoverage.DiscoverageRunner'
COVERAGE_OMIT_MODULES = ("*/admin.py", "*/migrations/*")
COVERAGE_EXCLUDE_PATTERNS = [
    r'def __unicode__\(self\):',
    r'def __str__\(self\):',
    r'def get_absolute_url\(self\):',
    r'from .* import .*',
    r'import .*',
    r'import .*',
    r'main\(\)',
]

