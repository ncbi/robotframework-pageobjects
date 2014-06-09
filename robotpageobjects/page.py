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
import uritemplate
import urllib2
import warnings
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from Selenium2Library import Selenium2Library
from Selenium2Library.locators.elementfinder import ElementFinder

from context import Context
import exceptions
from optionhandler import OptionHandler
from robot.utils import asserts


this_module_name = __name__


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
    def get_robot_aliases(cls, name, pageobject_name):
        """
        Gets an aliased name (with page object class substitued in either at the end
        or in place of the delimiter given the real method name.

        :param name: The name of the method
        :type name: str
        :returns: str
        """
        ret = []

        # Look through the alias dict. If there is an alias, add the aliased version to what is returned.
        if name in cls._aliases:
            ret.append(cls._aliases[name].replace(cls._alias_delimiter, "_" + pageobject_name + "_"))
        else:
            # If not aliased, add the keyword name with the page object name at the end.
            ret.append("%s_%s" % (name, pageobject_name))

        # Add the plain name of the keyword.
        ret.append(name)

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


class Override(str):
    pass


class SelectorsDict(dict):
    """
    Wrap dict to add the ability to enforce key uniqueness.
    """

    def merge(self, other_dict, from_subclass=False):
        """
        Merge in selectors from another dictionary. Don't allow duplicate keys.
        If from_subclass is True, allow subclasses to override parent classes.
        If they attempt to override without explicitly using the Override class,
        allow the override but raise a warning.
        :param other_dict: The dictionary to merge into the SelectorsDict object.
        :type other_dict: dict
        :returns: None
        """
        for key, value in other_dict.iteritems():
            if key in self:
                if from_subclass:
                    if not isinstance(key, Override):
                        warnings.warn("Key \"%s\" is defined in an ancestor class. \
                                       Using the value \"%s\" defined in the subclass.\
                                       To prevent this warning, use robotpageobjects.Override(\"%s\")." % (
                        key, value, key),
                                      exceptions.KeyOverrideWarning)

                else:
                    raise exceptions.DuplicateKeyError("Key \"%s\" is defined by two parent classes. \
                                            Only subclasses can override selector keys." % key)
            self[str(key)] = value


class _S2LWrapper(Selenium2Library):
    """
    Helper class that wraps Selenium2Library and manages the browser cache.
    """

    def __init__(self, *args, **kwargs):
        if not Context.in_robot():
            kwargs["run_on_failure"] = "Nothing"
            # S2L checks if its "run_on_failure" keyword is "Nothing". If it is, it won't do anything on failure.
            # We need this to prevent S2L from attempting to take a screenshot outside Robot.
        else:
            # If in Robot, we want to make sure Selenium2Library is imported so its keywords are available,
            # and so we can share its cache. When outside Robot, we won't share the cache with any import
            # of Selenium2Library. This could be done with a monkey-patch,
            # but we are punting until and unless this becomes an issue. See DCLT-708.
            Context.import_s2l()
            Context.monkeypatch_namespace()

        # Use Selenium2Library's cache for our page objects. That way you can run a keyword from any page object,
        # or from Selenium2Library, and not have to open a separate browser.
        self._shared_cache = Context.get_cache()
        super(_S2LWrapper, self).__init__(*args, **kwargs)
        if self._shared_cache is not None:
            self._cache = self._shared_cache
        Context.set_cache(self._cache)

    @property
    @not_keyword
    def driver(self):
        """
        Wrap the _current_browser() S2L method
        """
        try:
            return self._current_browser()
        except RuntimeError:
            return None

    @not_keyword
    def get_current_browser(self):
        """
        Legacy wrapper for self.driver
        """
        return self.driver


class _SelectorsManager(_S2LWrapper):
    """
    Class to manage selectors, which map to S2L locators.
    This allows page object authors to define a class-level dict.
    These selectors can be defined in any ancestor class, and
    are inherited. A subclass can override its parent's selectors:

    from robotpageobjects.page import Page, Override
    class Page1(Page):
        selectors = {"search button": "id=go",
              "input box": "xpath=//input[@id="foo"]"}

    class Page2(Page1):
        selectors = {Override("input box"): "id=bar"}
        ...

    And a Page2 object will have access to "search button", which maps to "id=go",
    and "input box", which maps to "id=bar".
    """
    selectors = {}

    def __init__(self, *args, **kwargs):
        """
        Set instance selectors according to the class hierarchy.
        See _get_class_selectors.
        """
        super(_SelectorsManager, self).__init__(*args, **kwargs)
        self.selectors = self._get_class_selectors()

    def _get_class_selectors(self):
        """
        Get the selectors from all parent classes and merge them,
        overriding any parent classes' selectors with subclasses'
        selectors.
        """

        def __get_class_selectors(klass):
            all_selectors = SelectorsDict()
            own_selectors = klass.__dict__.get("selectors", {})

            # Get all the selectors dicts defined by the bases
            base_dicts = [__get_class_selectors(base) for base in klass.__bases__ if hasattr(base, "selectors")]

            # Add the selectors for the bases to the return dict
            [all_selectors.merge(base_dict) for base_dict in base_dicts]

            # Update the return dict with this class's selectors, overriding the bases
            all_selectors.merge(own_selectors, from_subclass=True)
            return all_selectors

        return __get_class_selectors(self.__class__)

    def _is_locator_format(self, locator):
        """
        Ask Selenium2Library's ElementFinder if the locator uses
        one of its supported prefixes.
        :param locator: The locator to look up
        :type locator: str

        """
        finder = self._element_finder
        prefix = finder._parse_locator(locator)[0]
        return prefix is not None or locator.startswith("//")


    def _element_find(self, locator, *args, **kwargs):
        """
        Override built-in _element_find() method and map selectors. Try to use _element_find with the
        locator as is, then try, if a selector exists, try that.
        :param locator: The Selenium2Library-style locator (or IFT selector) to use
        :type locator: str
        :returns: WebElement or list
        """
        if locator in self.selectors:
            return super(_SelectorsManager, self)._element_find(self.selectors[locator], *args, **kwargs)
        else:
            try:
                return super(_SelectorsManager, self)._element_find(locator, *args, **kwargs)
            except ValueError:
                if not self._is_locator_format(locator):
                    # Not found, doesn't look like a locator, not in selectors dict
                    raise ValueError("\"%s\" looks like a selector, but it is not in the selectors dict." % locator)
                else:
                    raise

    @not_keyword
    def find_element(self, locator, required=True, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find single elements.
        TODO: Incorporate selectors API into this.
        :param locator: The Selenium2Library-style locator to use
        :type locator: str
        :param required: Optional parameter indicating whether an exception should be raised if no matches are found. Defaults to True.
        :type required: boolean
        :returns: WebElement instance
        """
        return self._element_find(locator, True, required, **kwargs)

    @not_keyword
    def find_elements(self, locator, required=True, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find multiple elements.
        TODO: Incorporate selectors API into this.
        :param locator: The Selenium2Library-style locator to use
        :type locator: str
        :param required: Optional parameter indicating whether an exception should be raised if no matches are found. Defaults to True.
        :type required: boolean
        :returns: WebElement instance
        """
        return self._element_find(locator, False, required, **kwargs)


class ComponentManager(_SelectorsManager):

    @not_keyword
    def get_instance(self, component_class):

        """ Gets a page component's instance.
        Use when you know you will be returning one
        instance of a component. If there are none on the page,
        returns None.

        :param component_class: The page component class
        """

        els = self.get_instances(component_class)
        try:
            ret = els[0]
        except KeyError:
            ret = None

        return ret

    @not_keyword
    def get_instances(self, component_class):

        """ Gets a page component's instances as a list
        Use when you know you will be returning at least two
        instances of a component. If there are none on the page
        returns an empty list.

        :param component_class: The page component class
        """
        return [component_class(reference_webelement) for reference_webelement in self.get_reference_elements(component_class)]

    @not_keyword
    def get_reference_elements(self, component_class):
        """
        Get a list of reference elements associated with the component class.
        :param component_class: The page component class
        """
        try:
            locator = self.locator
        except AttributeError:
            raise Exception("Must set a locator attribute or method on page component manager")

        # TODO: Yuch. If we call find_element, we get screenshot warnings relating to DCLT-659, DCLT-726,
        # browser isn't open yet, and when get_keyword_names uses inspect.getmembers, that calls
        # any methods defined as properties with @property, but the browser isn't open yet, so it
        # tries to create a screenshot, which it can't do, and thus throws warnings. Instead we call
        # the private _element_find, which is not a keyword.

        component_elements = self._element_find(self.locator, False, True)
        return component_elements


class _ComponentElementFinder(ElementFinder):
    """Overrides the element finder class that SE2Lib's
    _element_find uses so that we can pass the reference webelement
    instead of the driver. This allows us to limit our DOM search
    in components to the "reference webelement" instead of searching
    globally on the driver instance.
    """

    def __init__(self, webelement):

        super(_ComponentElementFinder, self).__init__()
        self._reference_webelement = webelement

    def find(self, browser, locator, tag=None):
        prefix = self._parse_locator(locator)[0]
        if prefix == "dom":
            return super(_ComponentElementFinder, self).find(browser, locator, tag=tag)
        else:
            return super(_ComponentElementFinder, self).find(self._reference_webelement, locator, tag=tag)

class Component(_SelectorsManager):

    def __init__(self, reference_webelement, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)
        self.reference_webelement = reference_webelement

        # Pass the root webelement to our overridden component finder class.
        self._element_finder = _ComponentElementFinder(self.reference_webelement)


class _BaseActions(_SelectorsManager):
    """
    Helper class that defines actions for PageObjectLibrary.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the options used by the actions defined in this class.
        """

        super(_BaseActions, self).__init__(*args, **kwargs)

        self._option_handler = OptionHandler()
        self._logger = Context.get_logger(this_module_name)
        self.selenium_speed = self._option_handler.get("selenium_speed") or 0
        self.set_selenium_speed(self.selenium_speed)
        self.selenium_implicit_wait = self._option_handler.get("selenium_implicit_wait") or 10
        self.set_selenium_implicit_wait(self.selenium_implicit_wait)

        self.baseurl = self._option_handler.get("baseurl")
        self.browser = self._option_handler.get("browser") or "phantomjs"

        self._sauce_options = [
            "sauce_username",
            "sauce_apikey",
            "sauce_platform",
            "sauce_browserversion",
            "sauce_device_orientation",
        ]
        for sauce_opt in self._sauce_options:
            setattr(
                self,
                sauce_opt,
                self._option_handler.get(sauce_opt)
            )

        self._attempt_sauce = self._validate_sauce_options()

        # There's only a session ID when using a remote webdriver (Sauce, for example)
        self.session_id = None

    def _validate_sauce_options(self):

        # If any sauce options are set, at least
        # username, apikey, and platform must be set, the rest are optional
        sauce = {}
        for attr in dir(self):
            if attr.startswith("sauce_"):
                sauce[attr] = getattr(self, attr)

        at_least_one_sauce_opt_set = any(sauce.values())
        if at_least_one_sauce_opt_set and (not sauce["sauce_username"] or
                                        not sauce["sauce_apikey"] or not sauce["sauce_platform"]):
            raise exceptions.MissingSauceOptionError("When running Sauce, need at " +
                                                     "least sauce-username, sauce-apikey, and sauce-platform " +
                                                  "options set.")

        # If we get here, tell the object that it's going to
        # attempt to use sauce and that all needed sauce options are
        # at least set.
        return at_least_one_sauce_opt_set

    @not_keyword
    def _resolve_url(self, *args):

        """
        Figures out the URL that a page object should open at.

        Called by open().
        """

        pageobj_name = self.__class__.__name__

        # We always need a baseurl set. This enforces parameterization of the
        # domain under test.

        if self.baseurl is None:
            raise exceptions.NoBaseUrlError("To open page object, \"%s\" you must set a baseurl." % pageobj_name)

        if len(args) > 0:
            # URI template variables are being passed in, so the page object encapsulates
            # a page that follows some sort of URL pattern. Eg, /pubmed/SOME_ARTICLE_ID.

            if self._is_url_absolute(self.uri_template):
                raise exceptions.AbsoluteUriTemplateError("The URI Template \"%s\" in \"%s\" is an absolute URL. "
                                                              "It should be relative and used with baseurl")

            # Parse the keywords, don't check context here, because we want
            # to be able to unittest outside of any context.
            uri_vars = {}

            # If passed in from Robot, it's a series of strings that need to be
            # parsed by the "=" char., otherwise it's a python dictionary, which is
            # the only argument.
            if isinstance(args[0], basestring):
                for arg in args:
                    split_arg = arg.split("=")
                    uri_vars[split_arg[0]] = split_arg[1]
            else:
                uri_vars = args[0]

            # Check that variables are correct and match template.
            for uri_var in uri_vars:
                if uri_var not in uritemplate.variables(self.uri_template):
                    raise exceptions.InvalidUriTemplateVariableError(
                        "The variable passed in, \"%s\" does not match "
                        "template \"%s\" for page object \"%s\"" % (uri_var,
                                                                    self
                                                                    .uri_template,
                                                                    pageobj_name))
            self.uri_vars = uri_vars
            return uritemplate.expand(self.baseurl + self.uri_template, uri_vars)

        # URI template not being passed in, so the page object might have a "uri" attribute
        # set which means the page object has a unique URL. Eg, Pubmed Home Page would have a
        # "url" attribute set to "/pubmed" given a baseurl of "http://domain".
        try:
            self.uri
        except AttributeError:
            raise exceptions.NoUriAttributeError(
                "Page object \"%s\" must have a \"uri\" attribute set." % pageobj_name)

        # Don't allow absolute uri attribute.
        if self._is_url_absolute(self.uri):
            raise exceptions.AbsoluteUriAttributeError(
                "Page object \"%s\" must not have an absolute \"uri\" attribute set. Use a relative URL "
                "instead." % pageobj_name)

        # urlparse.joinurl could be used, but it mucks with the url too much, esp file URLs
        return self.baseurl + self.uri

    @staticmethod
    def _is_url_absolute(url):
        if url[:7] in ["http://", "https://", "file://"]:
            return True
        else:
            return False

    def _log(self, *args):
        """
        Logs either to Robot or to a file if outside robot. If logging to a file,
        prints each argument delimited by tabs.
        """
        self._logger.info("\t".join([str(arg) for arg in args]))

    def go_to(self, *args):
        """
        Wrapper to make go_to method support uri templates.
        """
        resolved_url = self._resolve_url(*args)
        super(_BaseActions, self).go_to(resolved_url)
        return self

    def open(self, *args):
        """
        Wrapper for Selenium2Library's open_browser() that calls resolve_url for url logic and self.browser.
        It also deletes cookies after opening the browser.

        :param *args: A list or dictionary of variables mapping to a page object's uri_template. For example given a
        template like this::

                class MyPageObject(PageObject):
                    uri_template = "category/{category}"

                    ...

        calling in Python::

            ...
            my_page_object.open({"category": "home-and-garden"})

        or in Robot Framework::

           ...
           Open My Page Object  category=home-and-garden

        ...would open the browser at: `/category/home-and-garden`

        If no `uri_var` is passed the page object tries to open the browser at its uri attribute.


        :param delete_cookies: If set to True, deletes browser's cookies when called.
        :type delete_cookies: Boolean
        :returns: _BaseActions instance
        """
        resolved_url = self._resolve_url(*args)
        if self._attempt_sauce:
            remote_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (self.sauce_username, self.sauce_apikey)
            caps = getattr(webdriver.DesiredCapabilities, self.browser.upper())
            caps["platform"] = self.sauce_platform
            if self.sauce_browserversion:
                caps["version"] = self.sauce_browserversion
            if self.sauce_device_orientation:
                caps["device_orientation"] = self.sauce_device_orientation

            try:
                self.open_browser(resolved_url, self.browser, remote_url=remote_url, desired_capabilities=caps)
            except urllib2.HTTPError:
                raise exceptions.SauceConnectionError("Unable to connect to sauce labs. Check your username and "
                                                      "apikey")

            self.session_id = self.get_current_browser().session_id
            self._log("session ID: %s" % self.session_id)

        else:
            self.open_browser(resolved_url, self.browser)

        # Probably don't need this check here. We should log no matter
        # what and the user sets the log level. When we take this check out
        # also take out of base class __init__ parameter.
        self._log("open", self.__class__.__name__, str(self.get_current_browser()), resolved_url)

        return self

    def close(self):
        """
        Wrapper for Selenium2Library's close_browser.
        :returns: None
        """
        self.close_browser()
        return self

    def wait_for(self, condition):
        """
        Waits for a condition defined by the passed function to become True.
        :param condition: The condition to wait for
        :type condition: callable
        :returns: None
        """
        timeout = 10
        wait = WebDriverWait(self.get_current_browser(),
                             timeout)  #TODO: move to default config, allow parameter to this function too

        def wait_fnc(driver):
            try:
                ret = condition()
            except AssertionError as e:
                return False
            else:
                return ret

        wait.until(wait_fnc)
        return self

    @robot_alias("get_hash_on__name__")
    def get_hash(self):
        """
        Get the current location hash.
        :return: the current hash
        """
        url = self.get_location()
        parts = url.split("#")
        if len(parts) > 0:
            return "#".join(parts[1:])
        else:
            return ""

    @robot_alias("hash_on__name__should_be")
    def hash_should_be(self, expected_value):
        hash = self.get_hash()
        asserts.assert_equal(hash, expected_value)
        return self

    def is_visible(self, selector):
        """
        Get the visibility of an element by selector or locator
        :param selector: The selector or locator
        :type selector: str
        :return: whether the element is visible
        """
        return self._is_visible(selector)


class Page(_BaseActions):
    """
    Base RF page object.

    This class inherits from _BaseActions (which inherits from _S2LWrapper).
    These helper classes define the base actions and browser-wrapping behavior
    used by this class and its descendents.
    
    This class then provides the behavior used by the RF's dynamic API.
    Optional constructor arguments:
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the pageobject_name variable, which is used by the _Keywords class
        for determining aliases.
        """
        super(Page, self).__init__(*args, **kwargs)

        # If a name is not explicitly set with the name attribute,
        # get it from the class name.
        try:
            self.name
        except AttributeError:
            self.name = self._titleize(self.__class__.__name__)

    @staticmethod
    @not_keyword
    def _titleize(str):
        return re.sub(r"(\w)([A-Z])", r"\1 \2", str)

    @staticmethod
    @not_keyword
    def _underscore(str):
        return re.sub(r"\s+", "_", str)

    def get_keyword_names(self):
        """
        RF Dynamic API hook implementation that provides a list of all keywords defined by
        the implementing class. NB that this will not expose Selenium2Library's keywords.
        That is done (in Robot) by programmatically importing Selenium2Library. See __init__
        in _S2LWrapper.
        This method uses the _Keywords class to handle exclusions and aliases.
        :returns: list
        """

        # Return all method names on the class to expose keywords to Robot Framework
        keywords = []
        #members = inspect.getmembers(self, inspect.ismethod)


        # Look through our methods and identify which ones are Selenium2Library's
        # (by checking it and its base classes).
        for name in dir(self):
            try:
                obj = getattr(self, name)
            except:
                # Retrieving the attribute raised an exception - for example,
                # a property created with the @property decorator that
                # interacts with the driver
                continue

            # Don't look for non-methods.
            if not inspect.ismethod(obj):
                continue

            in_s2l_base = False
            func = obj.__func__  # Get the unbound function for the method
            # Check if that function is defined in Selenium2Library
            if func in Selenium2Library.__dict__.values():
                in_s2l_base = True
            else:
                # Check if the function is defined in any of Selenium2Library's direct base classes.
                # Note that this will not check those classes' ancestors.
                # TODO: Check all S2L's ancestors. DCLT-
                for base in Selenium2Library.__bases__:
                    if func in base.__dict__.values():
                        in_s2l_base = True
            # Don't add methods belonging to S2L to the exposed keywords.
            if in_s2l_base:
                continue
            elif inspect.ismethod(obj) and not name.startswith("_") and not _Keywords.is_method_excluded(name):
                # Add all methods that don't start with an underscore and were not marked with the
                # @not_keyword decorator.
                keywords += _Keywords.get_robot_aliases(name, self._underscore(self.name))
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
        meth = getattr(self, _Keywords.get_funcname_from_robot_alias(alias, self._underscore(self.name)))
        try:
            ret = meth(*args)
        except Exception, err:
            # Hardcode capture_page_screenshot. This is because run_on_failure
            # is being set to "Nothing" (DCLT-659 and DCLT-726).
            # TODO: After DCLT-827 is addressed, we can use run_on_failure again.
<<<<<<< HEAD
            # Try to take a screenshot. If it fails due to no browser being open,
            # just raise the original exception. A failed screenshot is just noise here.
            # QAR-47920
            try:
                self.capture_page_screenshot()
            except Exception, e:
                if e.message.find("No browser is open") != -1:
                    pass
            raise err
=======
            self.capture_page_screenshot()
            raise

        if isinstance(ret, Page):
            # DCLT-829
            # In Context, we keep track of the currently executing page.
            # That way, when a keyword is run, Robot (specifically, our monkeypatch
            # of Robot's Namespace class - see context.py) will know which library
            # to run a keyword on when there is a conflict.

            # All page object methods should return an instance of Page.
            # Look at the class name of that instance and use it to identify
            # which page object to set Context's pointer to.

            # Get the names of all currently imported libraries
            libnames = Context.get_libraries().keys()
            classname = ret.__class__.__name__

            for name in libnames:
                # If we find a match for the class name, set the pointer in Context.
                if name.split(".")[-1:][0] == classname:
                    Context.set_current_page(name)

        elif ret is None:
            raise exceptions.KeywordReturnsNoneError("Every page object method must have a return value.")

        return ret
>>>>>>> master
