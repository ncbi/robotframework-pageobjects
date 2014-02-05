
from ExposedBrowserSelenium2Library import ExposedBrowserSelenium2Library

import sys

class PageObjectLibrary(object):

    """
    Base RF page object. Imports ExposedBrowserSelenium2Library, which
    in turn exposes the browser object for use.

    Problem solved here is of using multiple page objects
    that import RF's Selenium2Library. Can't do that because it
    is responsible for managing browser. This way our page objects
    don't inherit from Selenium2Library, instead they simply use the
    browser instance.
    """

    def __init__(self):
        self.se = ExposedBrowserSelenium2Library._se_instance
