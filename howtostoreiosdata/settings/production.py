from .base import *

SECRET_KEY = get_env_variable("SECRET_KEY")

ALLOWED_HOSTS = ('....', )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'howtostoreiosdata',
        'USER': 'howtostoreiosdata',
        'PASSWORD': get_env_variable("DB_PASSWORD")
    }
}

