from .base import *

from ..log_filters import ManagementFilter

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    '192.168.1.4',
    'moonserver.doit.local',
]

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/var/lib/miningstatistic/db.sqlite3',
    }
}

# Logging

verbose = (
    "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(funcName)s [%(message)s]"
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'remove_migration_sql': {
            '()': ManagementFilter,
        },
    },
    'formatters': {
        'verbose': {
            'format': verbose,
            'datefmt': "%Y-%b-%d %H:%M:%S",
        },
    },
    'handlers': {
        'file': {
            'filters': [
                'remove_migration_sql',
            ],
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/httpd/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': [
                'file',
            ],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Email

# # Сообщения сохраняются в файл
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/var/log/httpd/django.mail'
# Поле 'From' если не указано
DEFAULT_FROM_EMAIL = 'no-reply@doit.local'
# Поле 'From' если отправлено ADMINS и MANAGERS
SERVER_EMAIL = 'contact@doit.local'
# Префикс темы сообщения
EMAIL_SUBJECT_PREFIX = '[Mining Statistic] '
# Поле 'To' если отправлено MANAGERS
MANAGERS = (('Us', 'ourselves@doit.local'),)
# Поле 'To' если отправлено ADMINS
ADMINS = (('Admin', 'admin@doit.local'),)

# # Сообщения отправляются по smtp
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# # Поле 'From' если не указано
# DEFAULT_FROM_EMAIL = 'my_support_mail@gmail.com'
# # Поле 'From' если отправлено ADMINS и MANAGERS
# SERVER_EMAIL = 'my_support_mail@gmail.com'
# # Префикс темы сообщения
# EMAIL_SUBJECT_PREFIX = '[Mining Statistic] '
# # Поле 'To' если отправлено MANAGERS
# MANAGERS = (('Us', 'my_secret_mail@gmail.com'),)
# # Поле 'To' если отправлено ADMINS
# ADMINS = (('Admin', 'my_secret_mail@gmail.com'),)
#
# # gmail
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'my_support_mail@gmail.com'
# EMAIL_HOST_PASSWORD = 'my_secret_password'
