import sys
import os
from Selenium2Library import Selenium2Library
from .optionhandler import OptionHandler

class ExposedBrowserSelenium2Library(Selenium2Library):

    """
    Base Selenium2 Library that helps expose the browser instance for use
    by page object classes. Page object classes do not inherit from this class,
    rather they import it in order to use the browser instance set in this class'
    __new__ special method.
    """

    def __new__(cls, *args, **kwargs):
        cls._se_instance = super(ExposedBrowserSelenium2Library, cls).__new__(cls, *args, **kwargs)
        return cls._se_instance
    
    def __init__(self, *args, **kwargs):
        super(ExposedBrowserSelenium2Library, self).__init__(*args, **kwargs)
        self._option_handler = OptionHandler()
    
    def _get_log_dir(self):
        """
        Override S2L's _get_log_dir to use our option handler for retrieving options.
        TODO: Modify S2L so that it uses an abstracted option handler and parametrize
        what option handling class to use.
        """
        logfile = self._option_handler.get("LOG FILE")
        if logfile != "NONE":
            return os.path.dirname(logfile)
        return self._option_handler.get("OUTPUTDIR")
