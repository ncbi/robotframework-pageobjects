"""
.. module:: PageObjectLibrary
   :platform: Unix, Mac, Windows
   :synopsis: Classes related to base page objects which can be used in the Robot Framework runner
   or outside the runner with plain unittest test cases. The base page object uses Robot Framework's
   Selenium2Library to interface with Selenium2 (Webdriver).

   How it works:

       - All page objects should inherit from :class:`PageObjectLibrary`.
       - :class:`PageObjectLibrary` inherits from :class:`_BaseActions`, which defines some important
       actions for all page objects.
       - :class:`_BaseActions` inherits from :class:`_S2LWrapper`, which in turn is responsible for
       1) getting the Selenium2Library instance, 2) interacting with Selenium2Library
       and 3) exposing Selenium2Library keywords to the page object instance.


.. moduleauthor:: Daniel Frishberg, Aaron Cohen <daniel.frishberg@nih.gov>, <aaron.cohen@nih.gov>

"""

import inspect
import re

from selenium.webdriver.support.ui import WebDriverWait

from robot.libraries.BuiltIn import BuiltIn
from robot import api as robot_api

from pageobjects.base.ExposedBrowserSelenium2Library import ExposedBrowserSelenium2Library
from optionhandler import OptionHandler

this_module_name = __name__
import logging


class _Keywords(object):
    """
    Class to isolate functionality related to
    keyword aliases.

    It provides two methods, which are exposed as decorators: `robot_alias` and `not_keyword`.
    These decorators can be used in derived page libraries to designate aliases for keywords,
    or to designate page object methods that should not be exposed as keywords.
    """
    _exclusions = {}
    _aliases = {}
    _alias_delimiter = "__name__"

    @classmethod
    def is_method_excluded(cls, name):
        """
        Checks whether a method is to be excluded from keyword names.
        :param name: The name of the method to check
        :type name: str
        :returns: boolean
        """
        return cls._exclusions.get(name, False)

    @classmethod
    def get_robot_alias(cls, name, pageobject_name):
        """
        Gets an aliased name (with page object class substitued in either at the end
        or in place of the delimiter given the real method name.

        :param name: The name of the method
        :type name: str
        :returns: str
        """
        # Look through the alias dict, return the aliased name for Robot
        if name in cls._aliases:
            ret = cls._aliases[name].replace(cls._alias_delimiter, "_" + pageobject_name + "_")
        else:
            # By default, page object name is appended to keyword
            ret = "%s_%s" % (name, pageobject_name)

        return ret

    @classmethod
    def get_funcname_from_robot_alias(cls, alias, pageobject_name):
        """
        Gets the real method name given a robot alias.
        :param alias: The name of the alias
        :type alias: str
        :param pageobject_name: The placeholder name to replace
        :type pageobject_name: str
        :returns: str
        """
        # Look for a stub matching the alias in the aliases dict.
        # If we find one, return the original func name.
        for fname, stub in cls._aliases.iteritems():
            if alias == stub.replace(cls._alias_delimiter, "_" + pageobject_name + "_"):
                return fname
            # We didn't find a match, so take the class name off the end.
        return alias.replace("_" + pageobject_name, "")

    @classmethod
    def not_keyword(cls, f):
        """
        Method to flag a public method as not a keyword. Wrapped by
        not_keyword function as a decorator. In is_method_excluded we'll check this.
        :param f: The function to designate as not a keyword
        :type f: callable
        :returns: callable
    
        """
        cls._exclusions[f.__name__] = True
        return f

    @classmethod
    def robot_alias(cls, stub):
        """
         A decorator. When a page object method is decorated with this
        the keyword exposed to Robot Framework is set to the name passed in.

        This is useful to change the aliasing from the page object method name
        to the Robot Keyword that's exposed.

        By default, the name of the page object class is appended to the page
        object method such that given a page object class name of GooglePageLibrary, its
        `search` method would become a "Search Google" keyword. If a "name" attribute is
        set on the page object instance, the value is used instead of the page object
        class name.

        But you can decorate the method and pass in any name, and it will be aliased
        according to what name is passed in. You can use the "__name__" delimeter to
        easily substitute the page object name (defined by a "name" atttribute set on
        the page object) into the keyword. For example::

            ...
            @robot_alias("search__name__for")
            def search(self, url):
                ...

        ...would alias the `search` method to "Search Google For".

        :param stub: The name of the original function (optionally containing a placeholder)
        :type stub: str
        :returns: callable
        """

        def makefunc(f):
            cls._aliases[f.__name__] = stub
            return f

        return makefunc


def not_keyword(f):
    """
    Decorator function to wrap _Keywords.not_keyword.

    Use this to tell Robot not to expose the decorated method
    as a keyword.

    :param f: The function to designate as not a keyword
    :type f: callable
    :returns: callable
    """
    return _Keywords.not_keyword(f)


def robot_alias(stub):
    """
    Decorator function to wrap _Keywords.robot_alias
    :param stub: The name of the original function (optionally containing a placeholder)
    :type stub: str
    :returns: callable
    """
    return _Keywords.robot_alias(stub)


class _S2LWrapper(object):
    """
    Helper class that defines the methods to be used in PageObjectLibrary that interact with Selenium2Library.
    This is used by _BaseActions, which is used by PageObjectLibrary. This class initializes the S2L instance
    used by a library. It also exposes the methods of the S2L instance as methods of its own instance
    by overriding __getattr__.
    
    
    Problem solved here is of using multiple page objects that import RF's Selenium2Library. Can't do that because it
    is responsible for managing browser. This way our page objects don't inherit from Selenium2Library, instead they
    simply use the browser instance.
    
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Selenium2Library instance.
        """
        # This call to object's __init__ shouldn't be here, right?
        #super(_S2LWrapper, self).__init__(*args, **kwargs)
        self._se = self._get_se_instance()

    def __getattr__(self, name):
        """
        Override the built-in __getattr__ method so that we expose
        Selenium2Library's methods.
        NB that __getattr__ is only called if the member can't be found normally.
        """
        try:
            attr = getattr(object.__getattribute__(self, "_se"), name)
        except Exception as e:
            # Pass along an AttributeError as though it came from this object.
            raise AttributeError("%r object has no attribute %r" % (self.__class__.__name__, name))
        return attr

    def _get_logger_outside_robot(self):
        logger = logging.getLogger(this_module_name)
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("po_log.txt")
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)
        return logger

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
            try:
                BuiltIn().import_library("Selenium2Library")
                se = BuiltIn().get_library_instance("Selenium2Library")

                # If in Robot, use Robot's logger
                self.logger = robot_api.logger
            except: # We're not running in Robot
                # We didn't find an instance in Robot, so see if one has been created by another Page Object.
                # Set up logger
                self.logger = self._get_logger_outside_robot()

                try:
                    # TODO: Pull this logic into ExposedBrowserSelenium2Library
                    se = ExposedBrowserSelenium2Library._se_instance
                except AttributeError:
                    # Create the instance
                    ExposedBrowserSelenium2Library()
                    se = ExposedBrowserSelenium2Library._se_instance
        return se


class _BaseActions(_S2LWrapper):
    """
    Helper class that defines actions for PageObjectLibrary
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the options used by the actions defined in this class.
        """
        super(_BaseActions, self).__init__(*args, **kwargs)
        self._option_handler = OptionHandler()
        self.selenium_speed = self._option_handler.get("selenium_speed") or .5
        self.set_selenium_speed(self.selenium_speed)
        self.baseurl = self._option_handler.get("baseurl")
        self.browser = self._option_handler.get("browser") or "phantomjs"

    def resolve_url(self, url=None):
        """
        Resolves the url to open for the page object's open method, depending on whether
        baseurl is set, url is passed etc.

        :param url: The URL, whether relative or absolute to resolve.
        :type url: str
        :returns: str
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
                if not self.homepage[:5] in ["http:", "file:"]:
                    raise Exception("Home page '%s' is invalid. You must set a baseurl" % self.homepage)
                else:
                    ret = self.homepage
        return ret

    def _log(self, *args):
        """
        Logs either to Robot or to a file if outside robot. If logging to a file,
        prints each argument delimited by tabs.
        """
        self.logger.info("\t".join(args))

    def open(self, url=None, delete_cookies=True):
        """
        Wrapper for Selenium2Library's open_browser() that calls resolve_url for url logic and self.browser.
        It also deletes cookies after opening the browser.
        :param url: Optionally specify a URL. If not passed in, resolve_url will default to the page object's homepage.
        :type url: str
        :param delete_cookies: If set to False, does not delete browser's cookies when called.
        :type delete_cookies: Boolean
        :returns: _BaseActions instance
        """
        resolved_url = self.resolve_url(url)
        self.open_browser(resolved_url, self.browser)

        # Probably don't need this check here. We should log no matter
        # what and the user sets the log level. When we take this check out
        # also take out of base class __init__ parameter.
        self._log("open", self.name, str(self._current_browser()), resolved_url)

        if delete_cookies:
            self.delete_all_cookies()
        return self

    def close(self):
        """
        Wrapper for Selenium2Library's close_browser.
        :returns: None
        """
        self.close_browser()

    def wait_for(self, condition):
        """
        Waits for a condition defined by the passed function to become True.
        :param condition: The condition to wait for
        :type condition: callable
        :returns: None
        """
        timeout = 10
        wait = WebDriverWait(self._current_browser(),
                             timeout) #TODO: move to default config, allow parameter to this function too

        def wait_fnc(driver):
            try:
                ret = condition()
            except AssertionError as e:
                return False
            else:
                return ret

        wait.until(wait_fnc)

    def _find_element(self, locator, first_only=True, required=True, **kwargs):
        """
        Helper method that wraps _element_find().
        :param locator: The Selenium2Library-style locator to use
        :type locator: str
        :param first_only: Optional parameter to restrict the search to the first element. Defaults to True.
        :type first_only: boolean
        :param required: Optional parameter to raise an exception if no matches are found. Defaults to True.
        :type required: boolean
        :returns: WebElement instance
        """
        return self._element_find(locator, first_only, required, **kwargs)

    @not_keyword
    def find_element(self, locator, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find single elements.
        TODO: Incorporate selectors API into this.
        :param locator: The Selenium2Library-style locator to use
        :type locator: str
        :param required: Optional parameter indicating whether an exception should be raised if no matches are found. Defaults to True.
        :type required: boolean
        :returns: WebElement instance
        """
        return self._find_element(locator, **kwargs)

    @not_keyword
    def find_elements(self, locator, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find multiple elements.
        TODO: Incorporate selectors API into this.
        :param locator: The Selenium2Library-style locator to use
        :type locator: str
        :param required: Optional parameter indicating whether an exception should be raised if no matches are found. Defaults to True.
        :type required: boolean
        :returns: WebElement instance
        """
        return self._find_element(locator, first_only=False, **kwargs)


class PageObjectLibrary(_BaseActions):
    """
    Base RF page object.

    This class inherits from _BaseActions (which inherits from _S2LWrapper).
    These helper classes define the base actions and browser-wrapping behavior
    used by this class and its descendents.
    
    This class then provides the behavior used by the RF's dynamic API.
    """
    browser = "firefox"

    def __init__(self, *args, **kwargs):
        """
        Initializes the pageobject_name variable, which is used by the _Keywords class
        for determining aliases.
        """
        super(PageObjectLibrary, self).__init__(*args, **kwargs)
        self.pageobject_name = self._get_pageobject_name()

    def _get_pageobject_name(self):
        """
        Gets the name that will be appended to keywords when using
        Robot by looking at the name attribute of the page object class.
        If no "name" attribute is defined, appends the name of the page object
        class.
        :returns: str
        """
        try:
            pageobject_name = re.sub(r"\s+", "_", self.name)
        except AttributeError:
            pageobject_name = self.__class__.__name__.replace("PageLibrary", "").lower()

        return pageobject_name

    def get_keyword_names(self):
        """
        RF Dynamic API hook implementation that provides a list of all keywords defined by
        the implementing class. NB that this will not expose Selenium2Library's keywords.
        This method uses the _Keywords class to handle exclusions and aliases.
        :returns: list
        """
        # Return all method names on the class to expose keywords to Robot Framework
        keywords = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and not name.startswith("_") and not _Keywords.is_method_excluded(name):
                keywords.append(_Keywords.get_robot_alias(name, self.pageobject_name))

        return keywords

    def run_keyword(self, alias, args):
        """
        RF Dynamic API hook implementation that maps method aliases to their actual functions.
        :param alias: The alias to look up
        :type alias: str
        :param args: The arguments for the keyword
        :type args: list
        :returns: callable
        """
        # Translate back from Robot Framework alias to actual method
        orig_meth = getattr(self, _Keywords.get_funcname_from_robot_alias(alias, self.pageobject_name))
        return orig_meth(*args)


