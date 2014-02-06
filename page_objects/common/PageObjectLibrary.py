
from page_objects.common.ExposedBrowserSelenium2Library import ExposedBrowserSelenium2Library

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
    def __init__(self, url=None):
        try:

            # Try to expose The RF's SE instance
            self.se = ExposedBrowserSelenium2Library._se_instance
        except AttributeError:
            # If it doesn't already exist, instantiate first.
            ExposedBrowserSelenium2Library()
            self.se = ExposedBrowserSelenium2Library._se_instance

    def open(self, url=None):
        if url:
            self.se.open_browser(url, self.browser)

        else:
            self.se.open_browser(self.homepage, self.browser)

        return self

    def close(self):
        self.se.close_browser()
