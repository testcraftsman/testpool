"""
Code that handles extensions.
"""
import sys
import unittest
import logging
import importlib
import pkgutil
import traceback
import testpool.settings


def onerror(name):
    """ Show module that fails to load. """
    logging.error("importing module %s", name)
    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)


def list_get():
    """ Return the list of extensions. """

    rtc = []

    for package in testpool.settings.PLUGINS:
        package = importlib.import_module(package)
        rtc += [item for _, item, _ in pkgutil.iter_modules(package.__path__)]

    return rtc


def api_ext_list():
    """ Look for command extensions. """

    api_exts = {}

    for package in testpool.settings.PLUGINS:
        logging.debug("loading api extension %s", package)
        package = importlib.import_module(package)

        for _, module, ispkg in pkgutil.walk_packages(
                package.__path__, package.__name__ + ".", onerror=onerror):
            if module.endswith("api") and not ispkg:
                logging.debug("loaded extension %s", module)

                path = module.split(".")
                product = path[-2]
                module = importlib.import_module(module)
                api_exts[product] = module

    return api_exts


class Testsuite(unittest.TestCase):
    """ Test ext interface. """
    def test_list(self):
        """ test_list. """

        api_exts = api_ext_list()
        self.assertTrue(api_exts)
        self.assertTrue("fake" in api_exts)

if __name__ == "__main__":
    unittest.main()
