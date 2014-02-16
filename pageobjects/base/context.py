from .ExposedBrowserSelenium2Library import ExposedBrowserSelenium2Library
from robot.libraries.BuiltIn import BuiltIn
from robot.running.context import EXECUTION_CONTEXTS
from robot import api as robot_api
import logging

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
    
    def in_robot(self):
        return EXECUTION_CONTEXTS.current is not None
    
    def get_se_instance(self):

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
            try:
                BuiltIn().import_library("Selenium2Library")
                se = BuiltIn().get_library_instance("Selenium2Library")
            except: # We're not running in Robot
                # We didn't find an instance in Robot, so see if one has been created by another Page Object.
                try:
                    # TODO: Pull this logic into ExposedBrowserSelenium2Library
                    se = ExposedBrowserSelenium2Library._se_instance
                except AttributeError:
                    # Create the instance
                    ExposedBrowserSelenium2Library()
                    se = ExposedBrowserSelenium2Library._se_instance
        return se

    def get_logger(self, module_name):
        if self.in_robot():
            return robot_api.logger
        else:
            return self._get_logger_outside_robot(module_name)
        
    @staticmethod
    def _get_logger_outside_robot(module_name):
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("po_log.txt")
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)
        return logger

