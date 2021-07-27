from .base import *  # noqa

DEBUG = True

INSTALLED_APPS += [  # noqa
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE += [  # noqa
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'verbose': {
            'format': '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        },
    },
    'handlers': {
        'console': {
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': {'console'},
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': os.environ.get('LOG_LEVEL', default='INFO'),
            'handlers': ['console'],
            'propagate': False,
        }
    },
}
