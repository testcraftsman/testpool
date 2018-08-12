"""
Content to validate configuration file.
"""
import os
import logging
import yaml
from easydict import EasyDict as edict
from testpool.core import logger

LOGGER = logger.create()


# pylint: disable=W0703
def is_valid_path(key, value):
    """ Throw exception if arg is not a path. """

    if not isinstance(value, str):
        raise ValueError("%s: must be a string" % key)
    return len(value) == 0


##
# Dictionary of valid content with functions that validate value.
VALID = {
    "tpldaemon": {
        "pool": {
            "log": is_valid_path
        }
    }
}
##


def level(cfg, valid, path):
    """ Compare cfg against valid options. """

    for (key, value) in cfg.iteritems():

        if not value and isinstance(valid[key], dict):
            continue
        new_path = key if not path else ".".join([path, key])
        if key not in valid:
            raise ValueError("illegal: key %s.%s" % (path, key))
        elif isinstance(cfg[key], dict):
            level(value, valid[key], new_path)
        else:
            try:
                valid[key](key, value)
            except Exception:
                raise ValueError("illegal: value %s: %s" % (key, value))


def check(cfg_file):
    """ Check cfg_file content. """

    if not os.path.isfile(cfg_file):
        return None

    logging.info("log file %s", cfg_file)
    with open(cfg_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        level(cfg, VALID, None)
        rtc = edict(cfg)
        logging.info("log file %s is valid", cfg_file)
        return rtc
