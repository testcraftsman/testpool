"""
  Provide database routing to testdb.

  This class handles the global parameter --database.
"""


# pylint: disable=R0201
# pylint: disable=W0613
class DefaultRouter(object):
    """ Assume current database is default unless set_db is called. """
    CURRENT = "default"

    @staticmethod
    def set_db(new_db):
        """ Set which database will handle future database actions. """
        DefaultRouter.CURRENT = new_db

    def db_for_read(self, model, **hints):
        """ Reads go CURRENT router. """
        return DefaultRouter.CURRENT

    def db_for_write(self, model, **hints):
        """ Writes always go to primary. """
        return DefaultRouter.CURRENT

    def allow_relation(self, obj1, obj2, **hints):
        """ Always allow relation. """
        return True

    def allow_migrate(self, _, app_label, model=None, **hints):
        """ All non-auth models end up in this pool. """
        return True
