import os
from Selenium2Library import Selenium2Library

class ExposedBrowserSelenium2Library(Selenium2Library):

    """
    Base Selenium2 Library that helps to expose the browser instance for use
    by page object classes. Page object classes do not inherit from this class,
    rather they import it in order to use the browser instance set in this class's
    __new__ special method.
    """

    def __new__(cls, *args, **kwargs):
        cls._se_instance = super(ExposedBrowserSelenium2Library, cls).__new__(cls, *args, **kwargs)
        return cls._se_instance
    
    def __init__(self, *args, **kwargs):
        # Set run_on_failure=None to prevent S2L from trying to take a screenshot.
        kwargs["run_on_failure"] = "Nothing"
        super(ExposedBrowserSelenium2Library, self).__init__(*args, **kwargs)
