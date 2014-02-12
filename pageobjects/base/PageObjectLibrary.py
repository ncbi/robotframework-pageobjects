from selenium.webdriver.support.ui import WebDriverWait
from pageobjects.base.ExposedBrowserSelenium2Library import ExposedBrowserSelenium2Library
from robot.libraries.BuiltIn import BuiltIn
import inspect
import re

import sys


class _Keywords(object):
    _exclusions = {}
    _aliases = {}
    _alias_delimiter = "__name__"
    
    @classmethod
    def is_method_excluded(cls, name):
        """
        Checks whether a method is to be excluded from keyword names.
        """
        return cls._exclusions.get(name, False)
    
    @classmethod
    def get_robot_alias(cls, name, pageobject_name):
        """
        Gets an aliased name (with page object class substitued in either at the end
        or in place of the delimiter given the real method name.
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
        Gets the real method name given a robot alias
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
        Decorator to flag a public method as not a keyword.
        In get_keyword_names and run_keyword we'll check this.
    
        TODO: find a better way to store the exclusions, possibly as a decorator class, or as a method of PageObjectLibrary.
        TODO: Pull logic of getting the exclusions into where the dictionary is handled.
        """
        cls._exclusions[f.__name__] = True
        return f
    
    @classmethod
    def robot_alias(cls, stub):
        """
        Decorator to map stubbed name to actual function
        for use by PageObject's (Robot dyanamic APIs) get_keyword_names and run_keyword
        methods.

        TODO: find a better way to store the aliases, maybe as a decorator class, or as a method of PageObjectLibrary.
        TODO: Pull logic of getting aliases out into where the dictionary is handled.
        """
        def makefunc(f):
            cls._aliases[f.__name__] = stub
            return f

        return makefunc

def not_keyword(f):
    """
    Decorator function to wrap _Keywords.not_keyword
    """
    return _Keywords.not_keyword(f)
def robot_alias(stub):
    """
    Decorator function to wrap _Keywords.robot_alias
    """
    return _Keywords.robot_alias(stub)


class _S2LWrapper(object):
    """
    Defines the methods to be used in PageObjectLibrary that interact with Selenium2Library.
    """
    
    def __init__(self, *args, **kwargs):
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
                # TODO: Pull this logic into ExposedBrowserSelenium2Library
                se = ExposedBrowserSelenium2Library._se_instance
            except AttributeError:
                # Create the instance
                ExposedBrowserSelenium2Library()
                se = ExposedBrowserSelenium2Library._se_instance
        return se


class _BaseActions(object):
    """
    Helper class that defines actions for PageObjectLibrary
    """

    def open(self, url=None):
        if url:
            self.open_browser(url, self.browser)

        else:
            self.open_browser(self.homepage, self.browser)

        return self

    def close(self):
        self.close_browser()

    def wait_for(self, condition):
        """
        Waits for a condition defined by the passed function to become True.
        """
        timeout = 10
        wait = WebDriverWait(self._current_browser(), timeout) #TODO: move to default config, allow parameter to this function too
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
        """
        return self._element_find(locator, first_only, required, **kwargs)

    @not_keyword
    def find_element(self, locator, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find single elements.
        TODO: Incorporate selectors API into this.
        """
        return self._find_element(locator, **kwargs)
    
    @not_keyword
    def find_elements(self, locator, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find multiple elements.
        TODO: Incorporate selectors API into this.
        """
        return self._find_element(locator, first_only=False, **kwargs)
    

class PageObjectLibrary(_S2LWrapper, _BaseActions):

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
    

    def __init__(self, *args, **kwargs):
        self.pageobject_name = self._get_pageobject_name()
        super(PageObjectLibrary, self).__init__(*args, **kwargs)

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
        sys.__stdout__.write("\n%s" % str(data))

    def get_keyword_names(self):
        # Return all method names on the class to expose keywords to Robot Framework
        keywords = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and not name.startswith("_") and not _Keywords.is_method_excluded(name):
                keywords.append(_Keywords.get_robot_alias(name, self.pageobject_name))

        return keywords

    def run_keyword(self, alias, args):
        # Translate back from Robot Framework alias to actual method
        orig_meth = getattr(self, _Keywords.get_funcname_from_robot_alias(alias, self.pageobject_name))
        return orig_meth(*args)
