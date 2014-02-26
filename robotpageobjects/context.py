import logging
from robot.libraries.BuiltIn import BuiltIn
from robot.running.context import EXECUTION_CONTEXTS
from robot import api as robot_api
from robot.conf import RobotSettings
from robot.variables import init_global_variables
from exposedbrowserselenium2library import ExposedBrowserSelenium2Library


class Context(object):
    """
    Encapsulates the logic for whether we're in Robot or not.
    It's a singleton.
    """
    _instance = None
    _new_called = 0
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

    @staticmethod
    def get_se_instance():
        """
        Gets the Selenoim2Library instance (which interfaces with SE)
        First it looks for an se2lib instance defined in Robot,
        which exists if a test has included a SE2Library.
    
        If the Se2Library is not included directly, then it looks for the
        instance stored on exposedbrowserselib, and if that's not found, it
        creates the instance.
        
        Note that this may not work unless this is called after Robot's Runner has started
        a suite, because the current context won't have been initialized.
        TODO: Determine whether this presents a problem for listeners.
        Using EXECUTION_CONTEXTS.current and checking if it's not None doesn't solve that problem,
        because we could still be running in Robot and simply not have a context yet.
        We need to handle that case without just returning a new S2L instance--probably raise
        and exception.
        """
        try:
            se = BuiltIn().get_library_instance("Selenium2Library")
        except (RuntimeError, AttributeError):
            # EBS2L imports OptionHandler, which imports Context, so we can't go back and import EBS2L at the top.
            try:
                BuiltIn().import_library("Selenium2Library")
                se = BuiltIn().get_library_instance("Selenium2Library")
            except: # We're not running in Robot
                # We didn't find an instance in Robot, so see if one has been created by another Page Object.
                try:
                    # TODO: Pull this logic into ExposedBrowserSelenium2Library
                    se = ExposedBrowserSelenium2Library._se_instance
                except AttributeError:
                    # Create the instance.
                    ExposedBrowserSelenium2Library()
                    se = ExposedBrowserSelenium2Library._se_instance
        return se

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

# Set up Robot's global variables so we get all the built-in default settings when we're outside Robot.
# We need this for Selenium2Library's _get_log_dir() method, among other things.
# TODO: DCLT-693: Put this handling in some other place.
# TODO: DCLT-659: Write test, confirm we're not breaking anything inside Robot, and that we are
#  not preventing the setting of certain CL options. We shouldn't be, since we use _get_opts_no_robot() below,
#  and then fall back if needed to GLOBAL_VARIABLES, which will always have Robot's default values.
if not Context.in_robot():
    init_global_variables(RobotSettings())
