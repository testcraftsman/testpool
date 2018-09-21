from split_settings.tools import optional, include

include(
    'components/base.py',
    'components/loggers.py',
    'components/global.py',

    ##
    # Local should be after global.py in order to override production 
    # values.
    optional('components/local.py'),
    'components/end.py',

    scope=globals()
)
