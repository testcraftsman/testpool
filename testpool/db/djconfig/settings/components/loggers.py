print "MARK: loggers"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
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
        'development': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/tmp/tpl-db.log',
            'formatter': 'verbose'
        },
        'production': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': '/var/log/testpool/tpl-db.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.testpool': {
            'handlers': ['console','development_logfile','production_logfile'],
         },
    }
}
