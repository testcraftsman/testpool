LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
	        'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'development': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/tmp/tpl-db.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'development'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        ##
        # Suppress database query in the logging, which is probably not needed
        # most of the time. 
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
        ##
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}


##
# Even if DEBUG is True, the django logging infrastructure will 
# attempt to initialize the handlers. In development, we do not have the 
# permission to modify /var/log
if not DEBUG:
   LOGGING["handlers"]["production"] = {
       'level': 'INFO',
       'filters': ['require_debug_false'],
       'class': 'logging.FileHandler',
       'filename': '/var/log/testpool/tpl-db.log',
       'formatter': 'verbose'
    }

if not DEBUG:
    LOGGING["loggers"]['django']['handlers'].append("production")
##
