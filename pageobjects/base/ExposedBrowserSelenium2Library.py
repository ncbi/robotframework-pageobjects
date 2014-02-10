from Selenium2Library import Selenium2Library
import sys

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
