from split_settings.tools import optional, include

include(
    'components/base.py',
    'components/pagination.py',
    optional('components/global.py'),

    ##
    # Local should be after product.py because if default value has not 
    # been defined in the DATABASE dictionary then it must be defined.
    'components/local.py',

    scope=globals()
)
