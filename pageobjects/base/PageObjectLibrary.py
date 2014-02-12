import inspect
import re
import sys

from selenium.webdriver.support.ui import WebDriverWait

from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger as robot_logger

from pageobjects.base.ExposedBrowserSelenium2Library import ExposedBrowserSelenium2Library
from optionhandler import OptionHandler


def robot_alias(stub):
    """
    Decorator to map stubbed name to actual function
    for use by PageObject's (Robot dyanamic APIs) get_keyword_names and run_keyword
    methods.

    TODO: find a better way to store the aliases, maybe as a class decorator.
    TODO: Pull logic of getting aliases out into where the dictionary is handled.
    """

    def makefunc(f):
        PageObjectLibrary._aliases[f.__name__] = stub
        return f

    return makefunc


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
    _alias_delimiter = "__name__"
    _aliases = {}

    def __init__(self, url=None):

        self.se = self._get_se_instance()

        # This should be paramterized
        self.pageobject_name = self._get_pageobject_name()
        self._option_handler = OptionHandler()
        self.selenium_speed = self._option_handler.get("selenium_speed") or .5
        self.se.set_selenium_speed(self.selenium_speed)
        self.baseurl = self._option_handler.get("baseurl")
        self.browser = self._option_handler.get("browser") or "phantomjs"
        self.logger = robot_logger


        # This is created for each page object..but it doesn't need to be.
        #self.output(self._option_handler._opts)

    def _get_se_instance(self):

        """
        Gets the Selenoim2Library instance (which interfaces with SE)
        First it looks for an se2lib instance defined in Robot,
        which exists if a test has included a SE2Library.

        If the Se2Library is not included directly, then it looks for the
        instance stored on exposedbrowserselib, and if that's not found, it
        creates the instance.
        """
        try:
            se = BuiltIn().get_library_instance("Selenium2Library")
        except (RuntimeError, AttributeError):
            # We didn't find an instance in Robot, so see if one has been created by another Page Object.
            try:
                se = ExposedBrowserSelenium2Library._se_instance
            except AttributeError:
                # Create the instance
                ExposedBrowserSelenium2Library()
                se = ExposedBrowserSelenium2Library._se_instance
        return se

    def _get_pageobject_name(self):

        """
        Gets the name that will be appended to keywords when using
        Robot by looking at the name attribute of the page object class.
        If no "name" attribute is defined, appends the name of the page object
        class.
        """
        try:
            pageobject_name = re.sub(r"\s+", "_", self.name)
        except AttributeError:
            pageobject_name = self.__class__.__name__.replace("PageLibrary", "").lower()

        return pageobject_name


    def output(self, data):
        sys.__stdout__.write(str(data))

    def _get_robot_alias(self, name):
        """
        Gets an aliased name (with page object class substitued in either at the end
        or in place of the delimiter given the real method name.
        """

        # Look through the alias dict, return the aliased name for Robot
        if name in PageObjectLibrary._aliases:
            ret = PageObjectLibrary._aliases[name].replace(self._alias_delimiter, "_" + self.pageobject_name + "_")

        else:
            # By default, page object name is appended to keyword
            ret = "%s_%s" % (name, self.pageobject_name)

        return ret

    def _get_funcname_from_robot_alias(self, alias):
        """
        Gets the real method name given a robot alias
        """
        # Look for a stub matching the alias in the aliases dict.
        # If we find one, return the original func name.
        for fname, stub in PageObjectLibrary._aliases.iteritems():
            if alias == stub.replace(self._alias_delimiter, "_" + self.pageobject_name + "_"):
                return fname
            # We didn't find a match, so take the class name off the end.
        return alias.replace("_" + self.pageobject_name, "")

    def get_keyword_names(self):
        # Return all method names on the class to expose keywords to Robot Framework
        keywords = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and not name.startswith("_"):
                keywords.append(self._get_robot_alias(name))

        return keywords

    def run_keyword(self, alias, args):
        # Translate back from Robot Framework alias to actual method
        orig_meth = getattr(self, self._get_funcname_from_robot_alias(alias))
        return orig_meth(*args)

    def resolve_url(self, url=None):
        """
        Resolves the url to open for the page object's open method, depending on whether
        baseurl is set, url is passed etc.

        :param url: The URL, whether relative or absolute to resolve.
        """
        if url:
            # URL is passed, if base url set, prefix it
            if self.baseurl:
                ret = self.baseurl + url
            else:
                ret = url
        else:
            if self.baseurl:
                # If no url passed and base url, then go to base url + homepage
                ret = self.baseurl + self.homepage
            else:
                if not self.homepage.startswith("http"):
                    raise Exception("Home page '%s' is invalid. You must set a baseurl" % self.homepage)
                else:
                    ret = self.homepage
        return ret

    def open(self, url=None):
        self.se.open_browser(self.resolve_url(url), self.browser)
        self.se.delete_all_cookies()

        return self

    def close(self):
        self.se.close_browser()

    def wait_for(self, condition):
        """
        Waits for a condition defined by the passed function to become True.
        """
        timeout = 10
        wait = WebDriverWait(self.se._current_browser(),
                             timeout) #TODO: move to default config, allow parameter to this function too

        def wait_fnc(driver):
            try:
                ret = condition()
            except AssertionError as e:
                return False
            else:
                return ret

        wait.until(wait_fnc)
