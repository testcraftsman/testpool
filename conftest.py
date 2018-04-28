"""
Py.test configuration.
"""

import logging
import testpool.core.database
testpool.core.database.init()

LOGGING = logging.getLogger("django.db.backends")
LOGGING.setLevel(logging.WARNING)

#  logging1 = logging.getLogger(None)
#  logging1.setLevel(logging.WARNING)
