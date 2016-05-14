"""
Common database api for builds.
"""
import logging
from testpool import models

CONTEXT = "build.default"


# pylint: disable=C0103
# pylint: disable=R0903
class BuildView(object):
    """ Used to biew build content on various pages.

    @param build  Part of the testsuite kvp is cached early, because
                  the assumbption is that it will be used several times.
    """
    def __init__(self, testsuite):
        self.id = testsuite.key_get("build")
        self.testsuite = testsuite

    def label(self):
        """ Label combining build and date. """
        return "%s" % (self.testsuite.timestamp.strftime("%m-%d-%Y %H:%M %p"))


# pylint: disable=W0622
def filter(product_key, branch_key=None):
    """ Return the list builds given the parameters.

    Build list is returned in newest to oldest.
    """

    logging.info("list build %s %s", product_key.value,
                 branch_key.value if branch_key else "*")
    (context, _) = models.Context.objects.get_or_create(name=CONTEXT)
    find = models.Testsuite.objects.filter(context=context, kvps=product_key)
    find = find.order_by("-timestamp")

    if branch_key:
        find = find.filter(kvps=branch_key)

    return find
