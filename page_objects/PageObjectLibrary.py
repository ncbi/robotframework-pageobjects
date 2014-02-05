
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
    browser = "firefox"
    def __init__(self, url=None, open_browser=True):
        try:

            # Try to expose The RF's SE instance
            self.se = ExposedBrowserSelenium2Library._se_instance
        except AttributeError:
            # If it doesn't already exist, instantiate first.
            ExposedBrowserSelenium2Library()
            self.se = ExposedBrowserSelenium2Library._se_instance


        # Allow instantiation of page object without opening a browser
        if url is not None and open_browser:
            self.se.open_browser(url, self.browser)
        elif open_browser and url is None:
            self.se.open_browser(self.homepage)
        else:
            pass

    def close(self):
        self.se.close_browser()