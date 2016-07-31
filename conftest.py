import logging
import testpool.core.database
testpool.core.database.init()

logging1 = logging.getLogger("django.db.backends")
logging1.setLevel(logging.WARNING)

#logging1 = logging.getLogger(None)
#logging1.setLevel(logging.WARNING)
