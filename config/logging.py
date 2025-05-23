import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        # "django": {
        #     "handlers": ["console"],
        #     "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        #     "propagate": False,
        # },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        # 'django.contrib.sessions': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        # },
    },
}