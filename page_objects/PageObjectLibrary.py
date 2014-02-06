
from ExposedBrowserSelenium2Library import ExposedBrowserSelenium2Library
import inspect

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
    _alias_delimiter = "__po__"

    def __init__(self, url=None):
        self.calling_class_name =  self.__class__.__name__.replace("PageLibrary", "").lower()

        try:

            # Try to expose The RF's SE instance
            self.se = ExposedBrowserSelenium2Library._se_instance
        except AttributeError:
            # If it doesn't already exist, instantiate first.
            ExposedBrowserSelenium2Library()
            self.se = ExposedBrowserSelenium2Library._se_instance

    def _get_robot_alias(self, name):
        """
        Gets an aliased name (with page object class substitued in either at the end
        or in place of the delimiter given the real method name.
        """
        if self._alias_delimiter in name:
            alias = name.replace(self._alias_delimiter, "_" + self.calling_class_name + "_")
        else:
            alias = "%s_%s" % (name, self.calling_class_name)

        return alias

    def _get_name_from_robot_alias(self, alias):
        """
        Gets the real method name given a robot alias
        """
        if alias.endswith(self.calling_class_name):
            name = alias.replace("_" + self.calling_class_name, "")
        else:
            name = alias.replace("_" + self.calling_class_name + "_", self._alias_delimiter)
        return name

    def get_keyword_names(self):
        # Return all method names on the class to expose keywords to Robot Framework
        keywords = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and not name.startswith("_"):
                keywords.append(self._get_robot_alias(name))

        return keywords

    def run_keyword(self, name, args):
        # Translate back from Robot Framework alias to actual method
        orig_meth = getattr(self,self._get_name_from_robot_alias(name))
        return orig_meth(*args)

    def open(self, url=None):
        if url:
            self.se.open_browser(url, self.browser)

        else:
            self.se.open_browser(self.homepage, self.browser)

        return self

    def close(self):
        self.se.close_browser()