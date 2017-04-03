"""
Common content for database setup.
"""
import sys
import os
import django
import testpool.settings


def init():
    """ Initialize database.
    @param log_dir Directory for storing log information.
    @param logical name of database to setup.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djconfig.settings")

    git_dir = os.path.abspath(os.path.join(__file__, "..", "..", "..", ".git"))
    if os.path.exists(git_dir):
        sys.path.insert(0, testpool.settings.TEST_DBSITE_DIR)
    else:
        sys.path.append(testpool.settings.TEST_DBSITE_DIR)

    # pylint: disable=W0612
    import djconfig.settings
    from django.conf import settings
    print "MARK: settings", settings
    django.setup()
