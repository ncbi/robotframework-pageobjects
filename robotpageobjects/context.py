import re
import logging
from robot.libraries.BuiltIn import BuiltIn
from robot.running.context import EXECUTION_CONTEXTS
from robot import api as robot_api
from robot.conf import RobotSettings
from robot.variables import init_global_variables
from Selenium2Library import Selenium2Library

__old_init = Selenium2Library.__init__.__func__
def __new_init(self, *args, **kwargs):
    kwargs["run_on_failure"] = "Nothing"
    return __old_init(self, *args, **kwargs)

Selenium2Library.__init__ = __new_init

def __get_keyword_names(self):
    import inspect
    ret = []
    methods = inspect.getmembers(self, inspect.ismethod)
    for name, meth in methods:
        if not name.startswith("_"):
            ret.append(name)
    return ret

Selenium2Library.get_keyword_names = __get_keyword_names

def __run_keyword(self, alias, args):
    meth = getattr(self, re.sub(r"\s+", "_", alias))
    try:
        return meth(*args)
    except Exception, err:
        self.capture_page_screenshot()
        raise

Selenium2Library.run_keyword = __run_keyword


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
        return EXECUTION_CONTEXTS.current is not None

    @classmethod
    def get_s2l_instance(cls):
        if cls._s2l_instance is not None:
            return cls._s2l_instance
        else:
            cls.import_s2l()
            return cls._s2l_instance

    @classmethod
    def import_s2l(cls):
        """
        Make sure that Selenium2Library has been imported by Robot.
        First try to get the existing instance. If that fails,
        tell Robot to import the library.
        """
        try:
            cls._s2l_instance = BuiltIn().get_library_instance("Selenium2Library")
        except:
            cls._s2l_instance = BuiltIn().import_library("Selenium2Library", "run_on_failure=Nothing")

    @classmethod
    def get_logger(cls, module_name):
        if cls.in_robot():
            return robot_api.logger
        else:
            return cls._get_logger_outside_robot(module_name)

    @staticmethod
    def _get_logger_outside_robot(module_name):
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("po_log.txt")
        #loglevel_as_str = OptionHandler().get("loglevel", "INFO")
        loglevel_as_str = "INFO"

        try:
            level = getattr(logging, loglevel_as_str)
        except AttributeError:
            raise Exception("No such loglevel exists: %s" % loglevel_as_str)
        fh.setLevel(level)
        logger.addHandler(fh)
        return logger

    @classmethod
    def set_keywords_exposed(cls):
        cls._keywords_exposed = True
        
    @classmethod
    def set_cache(cls, cache):
        cls._cache = cache
        
    @classmethod
    def get_cache(cls):
        if cls._cache is None:
            try:
                cls._cache = cls.get_s2l_instance()._cache
            except:
                pass
        return cls._cache

# Set up Robot's global variables so we get all the built-in default settings when we're outside Robot.
# We need this for Selenium2Library's _get_log_dir() method, among other things.
# TODO: DCLT-693: Put this handling in some other place.
# TODO: DCLT-659: Write test, confirm we're not breaking anything inside Robot, and that we are
#  not preventing the setting of certain CL options. We shouldn't be, since we use _get_opts_no_robot() below,
#  and then fall back if needed to GLOBAL_VARIABLES, which will always have Robot's default values.
if not Context.in_robot():
    init_global_variables(RobotSettings())
