from Selenium2Library.keywords import _browsermanagement
import re
import importlib
import inspect
import warnings

from robot.utils import asserts
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from Selenium2Library import Selenium2Library
from Selenium2Library.keywords.keywordgroup import KeywordGroupMetaClass

from . import abstractedlogger
from . import exceptions
from .context import Context
from .optionhandler import OptionHandler


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

    has_registered_s2l_keywords = False

    @classmethod
    def is_obj_keyword(cls, obj):
        """ Determines whether the given object is a keyword.
        """
        try:
            # It's either not a method or not an instance method, so
            # it can't be a keyword.
            name = obj.__name__
        except AttributeError:
            return False

        if inspect.isroutine(obj) and not name.startswith("_") and not _Keywords.is_method_excluded(name) and name not in ("get_keyword_names", "run_keyword"):
            return True

        else:
            return False

    @classmethod
    def is_obj_keyword_by_name(cls, name, inst):
        """ Determines whether a given name from the given class instance is a keyword.
        This is used by `get_keyword_names` in `robotpageobjects.page.Page` to decide
        what keyword names to report.
        :param name: The name of the member to check
        :type name: str
        :param inst: The class instance to check (such as a page object)
        :type inst: object
        """
        obj = None
        # If obj is a @property as oppose to a regular method or attribute,
        # its method will be called immediately. This could cause an attempt
        # to retrieve an element via webdriver, but when this method is called
        # no browser is open, so that will cause Selenium2Library's decorator
        # to attempt a screenshot - which will fail, because no browser is open.
        # To prevent this, we temporarily set inst._has_run_on_failure to True.
        # (_has_run_on_failure is used by Selenium2Library's decorator to prevent
        # redundant screenshot attempts.)
        inst._has_run_on_failure = True
        try:
            obj = getattr(inst, name)
        except Exception:
            inst._has_run_on_failure = False
            return False
        inst._has_run_on_failure = False

        return cls.is_obj_keyword(obj)

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


class Override(object):
    def __init__(self, obj):
        self.obj = obj


class KeyUniquenessDict(dict):
    """
    Wrap dict to add the ability to enforce key uniqueness and to allow values which can
    reference other values by key using the old python string formatting syntax

    dictionary = KeyUniquenessDict({
        'some_element' : 'xpath://html/body/div[1]/div',
        'another_element' : '%(some_element)s/span[3]',
    })

    print dictionary["some_element"]
    print dictionary["another_element"]
    """

    def __getitem__(self, item):
        return dict.__getitem__(self, item) % self

    def merge(self, other_dict, from_subclass=False):
        """
        Merge in values (selectors or components) from another dictionary.
        Don't allow duplicate keys.
        If from_subclass is True, allow subclasses to override parent classes.
        If they attempt to override without explicitly using the Override class,
        allow the override but raise a warning.
        :param other_dict: The dictionary to merge into the KeyUniquenessDict object.
        :type other_dict: dict
        :returns: None
        """
        for key, value in other_dict.iteritems():
            overridden = False
            if isinstance(key, Override):
                key = key.obj
                overridden = True
            if key in self:
                if from_subclass:
                    if not overridden:
                        warnings.warn("%s key \"%s\" is defined in an ancestor class. \
                                       Using the value \"%s\" defined in the subclass.\
                                       To prevent this warning, use robotpageobjects.Override(\"%s\")." % (
                            self.dict_type, key, value, key),
                                      exceptions.KeyOverrideWarning)

                else:
                    raise exceptions.DuplicateKeyError("Key \"%s\" is defined by two parent classes. \
                                            Only subclasses can override %s keys." % (key, self.dict_type))
            self.add(key, value)


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
            # This is for disambiguating keywords that are defined in multiple libraries.
            Context.set_current_page("Selenium2Library")

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


class SelectorsDict(KeyUniquenessDict):
    dict_type = "selector"
    def add(self, key, value):
        self[str(key)] = value


class ComponentsDict(KeyUniquenessDict):
    dict_type = "component"
    def add(self, key, value):
        self[key] = value

class _ComponentsManagerMeta(KeywordGroupMetaClass):
    @classmethod
    def _get_class_components(cls, bases, classdict):
        def get_components(cdict, cbases):
            """
            Recursive function to merge ancestor classes' components into this one's.
            We start with the class being created, so klass is None. The
            """
            all_components = ComponentsDict()
            own_components = cdict.get("components", {})

            # Get all the components dicts defined by the bases
            base_dicts = [get_components(base.__dict__, base.__bases__) for base in cbases if hasattr(base, "components")]

            # Add the components for the bases to the return dict
            [all_components.merge(base_dict) for base_dict in base_dicts]

            # Update the return dict with this class's selectors, overriding the bases
            all_components.merge(own_components, from_subclass=True)
            return all_components
        return get_components(classdict, bases)

    @classmethod
    def _set_components(cls, components, classdict):
        """

        """
        def mkfnc_plural(klass):
            """
            Create closure to avoid changing value of component_class
            """
            return lambda self: self.get_instances(klass)

        def mkfnc_singular(klass):
            """
            Singular version of mkfnc_plural
            """
            return lambda self: self.get_instance(klass)

        classdict["components"] = components

        for component_class in components:
            # Loop through components for this class. Normalize each component name,
            # and create plural and singular versions.
            name = re.sub("component$", "", component_class.__name__.lower())
            plural_name = name+"s"
            singular_name = name

            # Then, if not already defined, assign each name as a property. If defined, raise a warning.
            if plural_name not in classdict:
                classdict[plural_name] = property(mkfnc_plural(component_class))
            if singular_name not in classdict:
                classdict[singular_name] = property(mkfnc_singular(component_class))

    def __new__(cls, name, bases, classdict):
        components = cls._get_class_components(bases, classdict)
        cls._set_components(components, classdict)
        return KeywordGroupMetaClass.__new__(cls, name, bases, classdict)


class _ComponentsManager(object):
    """

    """
    __metaclass__ = _ComponentsManagerMeta

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
        try:
            return [component_class(reference_webelement) for reference_webelement in
                self.get_reference_elements(self.components[component_class])]
        except KeyError:
            raise exceptions.ComponentError("You tried to retrieve instances of a component not defined for this class.")

    @not_keyword
    def get_reference_elements(self, locator):
        """
        Get a list of reference elements associated with the component class.
        :param component_class: The page component class
        """

        # TODO: Yuch. If we call find_element, we get screenshot warnings relating to DCLT-659, DCLT-726,
        # browser isn't open yet, and when get_keyword_names uses inspect.getmembers, that calls
        # any methods defined as properties with @property, but the browser isn't open yet, so it
        # tries to create a screenshot, which it can't do, and thus throws warnings. Instead we call
        # the private _element_find, which is not a keyword.

        component_elements = self._element_find(locator, False, True)
        return component_elements


class _SelectorsManager(object):
    """
    Class to manage selectors, which map to S2L locators.
    This allows page object authors to define a class-level dict.
    These selectors can be defined in any ancestor class, and
    are inherited. A subclass can override its parent's selectors::

        from robotpageobjects.page import Page, Override
        class Page1(Page):
            selectors = {"search button": "id=go",
                  "input box": "xpath=//input[@id="foo"]"}

        class Page2(Page1):
            selectors = {Override("input box"): "id=bar"}
            ...

    And a Page2 object will have access to "search button", which maps to "id=go",
    and "input box", which maps to "id=bar".

    Selectors can also be templated which allows variables in locators::


        ...

        class MyPage(Page):

            selectors = {
                "nth result link": "xpath=id('product-list')/li/a[{n}]",
                ...
            }

            @robot_alias("click_result_link_on__name__")
            def click_result_link(self, index=0):
                xpath_index = index + 1
                locator = self.resolve_selector("nth result link", index=xpath_index)
                self.click_link(locator)
                return ProductPage()
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
        sels = __get_class_selectors(self.__class__)
        return sels

    def resolve_selector(self, selector, **kwargs):
        """ Expands a selector template and returns a locator
         for use by Selenium2Library methods like click_element().
         Pass the name of the selector template followed by keyword arguments
         matching the variables in the template.

         :param selector: The name of the selector
         :type selector: String

         Usage::

             class MyPage(Page):

                 self.selectors = {
                    "nth-para": "xpath=//p[{n}",
                    ...

                ...

                def click_nth_para(self, n):
                    loc = self.resolve_selector("nth-para", n=n)
                    self.click_element(loc)
        """

        template = self.selectors[selector]
        try:
            return template.format(**kwargs)
        except KeyError:
            raise exceptions.SelectorError("Variables {vars} don't match template {template}".format(vars=kwargs,
                                                                                                     template=template))

class _BaseActions(_S2LWrapper):
    """
    Helper class that defines actions for PageObjectLibrary.
    """

    _abstracted_logger = abstractedlogger.Logger()

    def __init__(self, *args, **kwargs):
        self.class__ = """
        Initializes the options used by the actions defined in this class.
        """
        #_ComponentsManager.__init__(self, *args, **kwargs)
        #_SelectorsManager.__init__(self, *args, **kwargs)
        super(_BaseActions, self).__init__(*args, **kwargs)

        self._option_handler = OptionHandler(self)
        self._is_robot = Context.in_robot()
        self.selenium_speed = self._option_handler.get("selenium_speed") or 0
        self.set_selenium_speed(self.selenium_speed)
        siw_opt = self._option_handler.get("selenium_implicit_wait")
        self.selenium_implicit_wait = siw_opt if siw_opt is not None else 10

        self.baseurl = self._option_handler.get("baseurl")

    def log(self, msg, level="INFO", is_console=True):
        """ Logs either to Robot log file or to a file called po_log.txt
        at the current directory.

        :param msg: The message to log
        :param level: The level to log at
        :type level: String corresponding to Robot or Python logging levels. See
        http://robot-framework.readthedocs.org/en/2.8.4/autodoc/robot.api.html?#log-levels for Robot log levels and
        http://docs.python.org/2/library/logging.html#levels for Python logging levels outside Robot.

        :param is_console: Whether or not to log to stdout
        :type is_console: Boolean

        Possible Robot levels are:

        - "WARN"
        - "INFO"
        - "DEBUG"
        - "TRACE"

        In Robot, you set the logging threshold using the --loglevel, or -L option
        to filter out logging chatter. For example, by default the logging level is
        set to "INFO" so if you logged "DEBUG" messages, the messages would not
        get reported.

        Robot logging messages get logged to stdout and to log.html.

        Outside of Robot, possible logging levels are:

         - "CRITICAL"
         - "ERROR"
         - "WARNING"
         - "INFO"
         - "DEBUG"
         - "NOSET"

        ...and you set the logging threshold level using the
        PO_LOG_LEVEL environment variable or log_level variable in a variable file.

        The Python logging module provides more logging levels than
        Robot provides; therefore, logging levels passed as strings to boththe log() method and the
        threshold level, are mapped to the closest supported Robot logging level and vice versa.

        The default threshold for both Robot and Python is "INFO".

        """

        return self._log(msg, self.name, level, is_console)

    def _log(self, msg, page_name, level="INFO", is_console=True):

        """ See :func:`log`."""
        self._abstracted_logger.log(msg, page_name, level, is_console)
        return self

    def wait_until_alert_is_present(self, timeout=None):
        alert_present = False
        self.wait_for(lambda: EC.alert_is_present(), timeout=timeout,
                      message="No alert was present after %s"
                              % self._format_timeout(timeout or self.selenium_implicit_wait))

    def wait_until_element_is_not_visible(self, locator, timeout=None, error=None):
        """Waits until element specified with `locator` is not visible.

        Fails if `timeout` expires before the element is not visible. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        """
        def check_visibility():
            visible = self._is_visible(locator)
            if not visible:
                return
            elif visible is None:
                return
            else:
                return error or "Element locator '%s' was still matched after %s" % (locator, self._format_timeout(timeout))
        self._wait_until_no_error(timeout, check_visibility)

    def wait_for(self, condition, timeout=None, message=''):
        """
        Waits for a condition defined by the passed function to become True.
        :param condition: The condition to wait for
        :type condition: callable
        :param timeout: How long to wait for the condition, defaults to the selenium implicit wait
        :type condition: number
        :param message: Message to show if the wait times out
        :type condition: string
        :returns: None
        """
        wait = WebDriverWait(self.get_current_browser(), timeout or self.selenium_implicit_wait)

        def wait_fnc(driver):
            try:
                ret = condition()
            except AssertionError as e:
                return False
            else:
                return ret

        wait.until(wait_fnc, message)
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

    def _element_find(self, locator, *args, **kwargs):
        """
        Override built-in _element_find() method and intelligently
        determine the locator for a passed-in selector name.

        Try to use _element_find with the
        locator as is, then if a selector exists, try that.

        ``locator`` can also be a WebElement if an element has been identified already
        and it is desired to perform actions on that element

        :param locator: The Selenium2Library-style locator, or IFT selector
                        or WebElement (if the element has already been identified).
        :type locator: str or WebElement
        :returns: WebElement or list
        """
        if isinstance(locator, WebElement):
            return locator

        # If wait is set, don't pass it along to the super classe's implementation, since it has none.
        if "wait" in kwargs:
            del kwargs["wait"]

        if locator in self.selectors:
            locator = self.resolve_selector(locator)

        try:
            return super(_BaseActions, self)._element_find(locator, *args, **kwargs)
        except ValueError:
            if not self._is_locator_format(locator):
                # Not found, doesn't look like a locator, not in selectors dict
                raise exceptions.SelectorError(
                    "\"%s\" is not a valid locator. If this is a selector name, make sure it is spelled correctly." % locator)
            else:
                raise

    @not_keyword
    def find_element(self, locator, required=True, wait=None, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find single elements.
        TODO: Incorporate selectors API into this.
        :param locator: The Selenium2Library-style locator to use
        :type locator: str
        :param required: Optional parameter indicating whether an exception should be raised if no matches are found. Defaults to True.
        :type required: boolean
        :param wait: Maximum Time in seconds to wait until the element exists. By default the implicit wait is 10
        seconds for any element finding method, including Se2lib methods. Passing a wait to find_element overrides
        this.
        :returns: WebElement instance
        """
        ret = self._element_find(locator, first_only=False, required=required, wait=wait, **kwargs)
        if len(ret) > 1:
            raise exceptions.SelectorError(
                "\"%s\" found more than one element. If this is expected, use \"find_elements\" instead" % locator)
        return ret[0]

    @not_keyword
    def find_elements(self, locator, required=True, wait=None, **kwargs):
        """
        Wraps Selenium2Library's protected _element_find() method to find multiple elements.
        TODO: Incorporate selectors API into this.
        :param locator: The Selenium2Library-style locator to use
        :type locator: str
        :param required: Optional parameter indicating whether an exception should be raised if no matches are found. Defaults to True.
        :type required: boolean
        :param wait: Maximum Time in seconds to wait until the element exists. By default the implicit wait is 10
        seconds for any element finding method, including Se2lib methods. Passing a wait to find_element overrides
        this.
        :returns: WebElement instance
        """
        return self._element_find(locator, first_only=False, required=required, wait=wait, **kwargs)

    @not_keyword
    def get_subclass_from_po_module(self, module_name, super_class, fallback_to_super=True):
        """Given `module_name`, try to import it and find in it a subclass of
        `super_class`. This is for dynamically resolving what page object to use
        for, say, a search that can bring up multiple types of search result page.
        :param module_name: The name of the module to look for.
        :type module_name: str
        :param super_class: The class to look for subclasses of.
        :type super_class: type
        :param fallback_to_super: Whether to default to returning `super_class` if module `module_name`
         cannot be imported.
        :returns: type
        """
        try:
            po_mod = importlib.import_module(module_name)
        except ImportError:
            if fallback_to_super:
                return super_class
        else:
            for name, obj in inspect.getmembers(po_mod):
                if inspect.isclass(obj) and issubclass(obj, super_class) and obj != super_class:
                    return obj
        raise exceptions.PageSelectionError("You need to have the %s package installed to go to a %s page,"
                                            "and the package needs to have a subclass of %s."
                                            % (module_name, module_name, super_class))

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

    def location_should_be(self, expected_url):
        """
        Wrapper for Selenium2Library's location_should_be() method.  Allows matching against the
        baseurl if a partial url is given.

        :param url: Either complete url or partial url to be validated against
        :type url: str
        :returns: True or False
        """
        if re.match("^(\w+:)?//", expected_url):
            # Simply compares with the expected url as it starts with http
            return super(_BaseActions, self).location_should_be(expected_url), self
        else:
            # This condition is for partial url,
            # as the regular expression fails it is considered as partial url
            # and hence it is appended to the baseurl
            return super(_BaseActions, self).location_should_be(self.baseurl+ expected_url), self
