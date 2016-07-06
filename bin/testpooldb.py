#!/usr/bin/env python
"""
Administrative management operations.
"""
import os
import sys
import testpool.settings


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djconfig.settings")
    sys.path.append(testpool.settings.TEST_DBSITE_DIR)

    # pylint: disable=C0411
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
