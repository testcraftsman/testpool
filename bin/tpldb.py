#!/usr/bin/env python
"""
Administrative management operations.
"""
import os
import sys

def env_setup():
    """ Main entry point.

    If calling tbd from within a .git clone append the appropriate
    testpool directory clone otherwise python content is stored
    under the normal site-packages.
    """

    ##
    # If the git directory exists, at this location then this script
    # is part of a git clone.
    git_dir = os.path.abspath(os.path.join(__file__, "..", "..", ".git"))
    if os.path.exists(git_dir):
        ##
        # This path is necessary to load anything under testpool clone.
        testpool_dir = os.path.abspath(os.path.join(__file__, "..", ".."))
        sys.path.insert(0, testpool_dir)


if __name__ == "__main__":

    env_setup()
    import testpool.settings

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djconfig.settings")
    sys.path.append(testpool.settings.TEST_DBSITE_DIR)

    # pylint: disable=C0411
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
