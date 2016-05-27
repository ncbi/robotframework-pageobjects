from robot.libraries.BuiltIn import BuiltIn
from robot.running.context import EXECUTION_CONTEXTS
from .monkeypatches import do_monkeypatches

do_monkeypatches()


class Context(object):
    """
    Encapsulates the logic for whether we're in Robot or not.
    It's a singleton.
    """
    _instance = None
    _s2l_instance = None
    _new_called = 0
    _keywords_exposed = False
    _cache = None
    _current_page = None
    def __new__(cls, *args, **kwargs):
        """
        Make this object a singleton. We're using this in optionhandler as well,
        so we should probably create a decorator. I'm surprised Python doesn't
        provide one. Alternatively we could just make everything class methods
        on this class.
        """
        if cls._instance is None:
            cls._instance = super(Context, cls).__new__(cls, *args, **kwargs)
            cls._new_called += 1

        return cls._instance

    @staticmethod
    def in_robot():
        try:
            BuiltIn().get_variables()
            return True
        except:
            return False

    @classmethod
    def set_keywords_exposed(cls):
        cls._keywords_exposed = True

    @classmethod
    def set_cache(cls, cache):
        cls._cache = cache

    @classmethod
    def get_cache(cls):
        return cls._cache

    @classmethod
    def set_current_page(cls, name):
        BuiltIn().set_library_search_order(name)

    @classmethod
    def get_libraries(cls):
        return [lib.name for lib in EXECUTION_CONTEXTS.current.namespace.libraries]
