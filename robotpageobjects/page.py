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
from __future__ import print_function
import inspect
import re
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import decorator
from Selenium2Library import Selenium2Library
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import uritemplate

from .base import _ComponentsManagerMeta, not_keyword, robot_alias, _BaseActions, _Keywords, Override, _SelectorsManager, _ComponentsManager
from . import exceptions
from .context import Context
from .sig import get_method_sig


# determine if libdoc is running to avoid generating docs for automatically generated aliases
ld = 'libdoc'
in_ld = any([ld in str(x) for x in inspect.stack()])

class _PageMeta(_ComponentsManagerMeta):
    """Meta class that allows decorating of all page object methods
    with must_return decorator. This ensures that all page object
    methods return something, whether it's a page object or other
    appropriate value. We must do this in a meta class since decorating
    methods and returning a wrapping function then rebinding that to the
    page object is tricky. Instead the binding of the decorated function in the
    meta class happens before the class is instantiated.
    """

    @staticmethod
    def _must_return(f, *args, **kwargs):
        ret = f(*args, **kwargs)
        if ret is None:
            raise exceptions.KeywordReturnsNoneError(
                "You must return either a page object or an appropriate value from the page object method, "
                "'%s'" % f.__name__)
        else:
            return ret

    @classmethod
    def must_return(cls, f):
        # Use decorator module to preserve docstings and signatures for Sphinx
        return decorator.decorator(cls._must_return, f)

    @classmethod
    def _fix_docstrings(cls, bases):
        """ Called from _PageMeta's __new__ method.
        For Sphinx auto-API docs, fixes up docstring for keywords that
        take locators by
        redefining method signature, replacing "locator" parameter with
        "selector_or_locator". Does this by taking advantage of Sphinx's
        autodoc_signature feature, which allows you to override documented
        function signature by putting override as first line in docstring.

        Also replaces references to "locator" in rest of docstring with
        "selector or locator".

        :param bases: A tuple of base classes a particular class
        inherits from.
        """
        for base in bases:

            # Don't fix up a class more than once.
            if not hasattr(base, "_fixed_docstring"):

                for member_name, member in inspect.getmembers(base):
                    if _Keywords.is_obj_keyword(member):
                        try:
                            # There's a second argument
                            second_arg = inspect.getargspec(member)[0][1]
                        except IndexError:
                            continue

                        orig_doc = inspect.getdoc(member)
                        if orig_doc is not None and second_arg == "locator":
                            orig_signature = get_method_sig(member)
                            fixed_signature = orig_signature.replace("(self, locator", "(self, selector_or_locator")
                            if orig_doc is not None:
                                # Prepend fixed signature to docstring
                                # and fix references to "locator".
                                fixed_doc = fixed_signature + "\n\n" + orig_doc
                                fixed_doc = fixed_doc.replace("`locator`", "`selector` or `locator`")
                                fixed_doc = fixed_doc.replace(" locator ", " selector or locator ")
                                member.__func__.__doc__ = fixed_doc

                base._fixed_docstring = True

    def __new__(cls, name, bases, classdict):
        # Don't do inspect.getmembers since it will try to evaluate functions
        # that are decorated as properties.
        for member_name, obj in classdict.iteritems():
            if _Keywords.is_obj_keyword(obj):
                classdict[member_name] = cls.must_return(classdict[member_name])

        cls._fix_docstrings(bases)
        return _ComponentsManagerMeta.__new__(cls, name, bases, classdict)


class Page(_BaseActions, _SelectorsManager, _ComponentsManager):
    """
    This is the base Page Object from which all other Page Objects should inherit.
    It contains all base Selenium2Library actions and browser-wrapping behavior
    used by this class and its descendents.

    It is a robotframework library which implements the dynamic API.
    """
    __metaclass__ = _PageMeta
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        """
        Initializes the pageobject_name variable, which is used by the _Keywords class
        for determining aliases.
        """
        for base in Page.__bases__:
            base.__init__(self)

        self.browser = self._option_handler.get("browser") or "phantomjs"
        self.service_args = self._parse_service_args(self._option_handler.get("service_args", ""))

        self._sauce_options = [
            "sauce_username",
            "sauce_apikey",
            "sauce_platform",
            "sauce_browserversion",
            "sauce_device_orientation",
            "sauce_screenresolution",
        ]
        for sauce_opt in self._sauce_options:
            setattr(self, sauce_opt, self._option_handler.get(sauce_opt))

        self._attempt_sauce = self._validate_sauce_options()

        # There's only a session ID when using a remote webdriver (Sauce, for example)
        self.session_id = None

        # If a name is not explicitly set with the name attribute,
        # get it from the class name.
        try:
            self.name
        except AttributeError:
            self.name = self._titleize(self.__class__.__name__)

        # Allow setting of uri_template or uri, but make them the same internally
        if hasattr(self, 'uri_template'):
            self.uri = self.uri_template
        # Set a default uri in case one is not set in the Page
        elif not hasattr(self, 'uri'):
            self.uri = '/'

    @staticmethod
    @not_keyword
    def _titleize(str):
        """
        Converts camel case to title case
        :param str: camel case string
        :return: title case string
        """
        return  re.sub('([a-z0-9])([A-Z])', r'\1 \2', re.sub(r"(.)([A-Z][a-z]+)", r'\1 \2', str))

    @staticmethod
    @not_keyword
    def _underscore(str):
        return re.sub(r"\s+", "_", str)

    @not_keyword
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
            is_keyword = _Keywords.is_obj_keyword_by_name(name, self)
            if is_keyword:
                obj = getattr(self, name)
                in_s2l_base = False
                try:
                    func = obj.__func__  # Get the unbound function for the method
                except AttributeError:
                    # ignore static methods included in libraries
                    continue
                # Check if that function is defined in Selenium2Library
                if func not in self.__class__.__dict__.values():
                    if name in Selenium2Library.__dict__.keys():
                        in_s2l_base = True
                    else:
                        # Check if the function is defined in any of Selenium2Library's direct base classes.
                        # Note that this will not check those classes' ancestors.
                        # TODO: Check all S2L's ancestors. DCLT-
                        for base in Selenium2Library.__bases__:
                            if name in base.__dict__.keys():
                                in_s2l_base = True
                # Don't add methods belonging to S2L to the exposed keywords.
                if in_s2l_base and (in_ld or _Keywords.has_registered_s2l_keywords):
                    continue
                elif inspect.ismethod(obj) and not name.startswith("_") and not _Keywords.is_method_excluded(name):
                    # Add all methods that don't start with an underscore and were not marked with the
                    # @not_keyword decorator.
                    if not in_ld:
                        keywords += _Keywords.get_robot_aliases(name, self._underscore(self.name))
                    else:
                        keywords.append(name)
        _Keywords.has_registered_s2l_keywords = True

        return keywords

    def _attempt_screenshot(self):
            try:
                self.capture_page_screenshot()
            except Exception as e:
                if e.message.find("No browser is open") != -1:
                    pass

    @not_keyword
    def run_keyword(self, alias, args, kwargs):
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
            ret = meth(*args, **kwargs)
        except:
            # Pass up the stack, so we see complete stack trace in Robot trace logs
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
            libnames = Context.get_libraries()
            classname = ret.__class__.__name__

            for name in libnames:
                # If we find a match for the class name, set the pointer in Context.
                if name.split(".")[-1:][0] == classname:
                    Context.set_current_page(name)

        # The case of raising an exception if a page object method returns None is handled
        # by Page's meta class, because we need to raise this exception for Robot and
        # outside Robot.

        # If nothing was returned and the method was defined in Selenium2Library,
        # just return self. That way, we exempt Selenium2Library from the "must_return"
        # requirement, but still know what page we're on. (For Selenium2Library keywords
        # that go to another page, we'll just assume we're using the same PO.)
        if ret is None:
            func = meth.__func__
            if meth in Selenium2Library.__dict__.values():
                ret = self
            else:
                for base in Selenium2Library.__bases__:
                    if meth.__func__ in base.__dict__.values():
                        ret = self
                        break
        return ret

    @not_keyword
    def get_keyword_documentation(self, kwname):
        """
        RF Dynamic API hook implementation that exposes keyword documentation to the libdoc tool

        :param kwname: a keyword name
        :return: a documentation string for kwname
        """
        if kwname == '__intro__':
            docstring = self.__doc__ if self.__doc__ else ''
            s2l_link = """\n
            All keywords listed in the Selenium2Library documentation are also available in this Page Object.
            See http://rtomac.github.io/robotframework-selenium2library/doc/Selenium2Library.html
            """
            return docstring + s2l_link
        kw = getattr(self, kwname, None)
        alias = ''
        if kwname in _Keywords._aliases:
            alias = '*Alias: %s*\n\n' % _Keywords.get_robot_aliases(kwname, self._underscore(self.name))[0].replace('_', ' ').title()
        docstring = kw.__doc__ if kw.__doc__ else ''
        docstring = re.sub(r'(wrapper)', r'*\1*', docstring, flags=re.I)
        return alias + docstring

    @not_keyword
    def get_keyword_arguments(self, kwname):
        """
        RF Dynamic API hook implementation that exposes keyword argspecs to the libdoc tool

        :param kwname: a keyword name
        :return: a list of strings describing the argspec
        """
        kw = getattr(self, kwname, None)
        if kw:
            args, varargs, keywords, defaults = inspect.getargspec(kw)
            defaults = dict(zip(args[-len(defaults):], defaults)) if defaults else {}
            arglist = []
            for arg in args:
                if arg != 'self':
                    argstring = arg
                    if arg in defaults:
                        argstring += '=%s' % defaults[arg]
                    arglist.append(argstring)
            if varargs:
                arglist.append('*args')
            if keywords:
                arglist.append('**keywords')
            return arglist
        else:
            return ['*args']

    def _parse_service_args(self, service_args):
        return [arg.strip() for arg in service_args.split(" ") if arg.strip() != ""]

    def _validate_sauce_options(self):
        """
        Check if user wants to use sauce and make sure all required options are given
        :return: bool (does user want to use sauce?)
        """
        trigger_opts = {'platform': None, 'browserversion': None, 'device_orientation': None}
        for trigger_opt in trigger_opts.keys():
            trigger_opts[trigger_opt] = getattr(self, 'sauce_' + trigger_opt)
        sauce_desired = any(trigger_opts.values())

        if sauce_desired:
            required_opts = {'username': None, 'apikey': None, 'platform': None}
            for required_opt in required_opts.keys():
                required_opts[required_opt] = getattr(self, 'sauce_' + required_opt)
            have_all_required = all(required_opts.values())

            if not have_all_required:
                raise exceptions.MissingSauceOptionError(
                    "When running Sauce, need at least sauce_username, sauce_apikey, and sauce_platform options set.")
            if self.browser == 'phantomjs':
                raise exceptions.MissingSauceOptionError("When running Sauce, browser option should not be phantomjs.")

        return sauce_desired

    @staticmethod
    def _vars_match_template(template, vars):
        """Validates that the provided variables match the template.
        :param template: The template
        :type template: str
        :param vars: The variables to match against the template
        :type vars: tuple or list
        :returns: bool"""
        keys = list(vars.keys())
        keys.sort()
        template_vars = list(uritemplate.variables(template))
        template_vars.sort()
        return template_vars == keys

    @not_keyword
    def _resolve_url(self, *args):

        """
        Figures out the URL that a page object should open at.

        Called by open().
        """
        pageobj_name = self.__class__.__name__

        # determine type of uri attribute
        if hasattr(self, 'uri'):
            uri_type = 'template' if re.search('{.+}', self.uri) else 'plain'
        else:
            raise exceptions.UriResolutionError("Page object \"%s\" must have a \"uri\" attribute set." % pageobj_name)

        # Don't allow absolute uri attribute.
        if self._is_url_absolute(self.uri):
            raise exceptions.UriResolutionError(
                "Page object \"%s\" must not have an absolute \"uri\" attribute set. Use a relative URL "
                "instead." % pageobj_name)

        # We always need a baseurl set. This enforces parameterization of the
        # domain under test.

        if self.baseurl is None:
            raise exceptions.UriResolutionError("To open page object, \"%s\" you must set a baseurl." % pageobj_name)

        elif len(args) > 0 and hasattr(self, "uri") and self._is_url_absolute(self.uri):
            # URI template variables are being passed in, so the page object encapsulates
            # a page that follows some sort of URL pattern. Eg, /pubmed/SOME_ARTICLE_ID.

            raise exceptions.UriResolutionError("The URI Template \"%s\" in \"%s\" is an absolute URL. "
                                                "It should be relative and used with baseurl" %
                                                (self.uri, pageobj_name))

        if len(args) > 0:
            # the user wants to open a non-default uri
            uri_vars = {}

            first_arg = args[0]
            if not self._is_robot:
                if isinstance(first_arg, str):
                    # In Python, if the first argument is a string and not a dict, it's a url or path.
                    arg_type = "url"
                else:
                    arg_type = "dict"
            elif self._is_robot:
                # We'll always get string args in Robot
                if self._is_url_absolute(first_arg) or first_arg.startswith("/"):
                    arg_type = "url"
                else:
                    arg_type = "robot"

            if arg_type != "url" and hasattr(self, "uri") and uri_type == 'plain':
                raise exceptions.UriResolutionError(
                    "URI %s is set for page object %s. It is not a template, so no arguments are allowed." %
                    (self.uri, pageobj_name))

            if arg_type == "url":
                if self._is_url_absolute(first_arg):
                    # In Robot, the first argument is always a string, so we need to check if it starts with "/" or a scheme.
                    # (We're not allowing relative paths right now._
                    return first_arg
                elif first_arg.startswith("//"):
                    raise exceptions.UriResolutionError("%s is neither a URL with a scheme nor a relative path"
                                                        % first_arg)
                else:  # starts with "/"
                    # so it doesn't need resolution, except for appending to baseurl and stripping leading slash
                    # if it needed: i.e., if the base url ends with "/" and the url starts with "/".

                    return re.sub("\/$", "", self.baseurl) + first_arg
            elif arg_type == "robot":
                # Robot args need to be parsed as "arg1=123", "arg2=foo", etc.
                for arg in args:
                    split_arg = arg.split("=")
                    uri_vars[split_arg[0]] = "=".join(split_arg[1:])
            else:
                # dict just contains the args as keys and values
                uri_vars = args[0]

            # Check that variables are correct and match template.
            if not self._vars_match_template(self.uri, uri_vars):
                raise exceptions.UriResolutionError(
                    "The variables %s do not match template %s for page object %s"
                    % (uri_vars, self.uri, pageobj_name)
                )
            self.uri_vars = uri_vars
            return uritemplate.expand(self.baseurl + self.uri, uri_vars)
        else:
            if uri_type == 'template':
                raise exceptions.UriResolutionError('%s has uri template %s , but no arguments were given to resolve it' %
                                                    (pageobj_name, self.uri))
            # the user wants to open the default uri
            return self.baseurl + self.uri

    @staticmethod
    def _is_url_absolute(url):
        """
        We're making the scheme mandatory, because webdriver can't handle just "//".
        """
        return re.match("^(\w+:(\d+)?)\/\/", url) is not None

    def go_to(self, *args):
        """
        Wrapper to make go_to method support uri templates.
        """
        resolved_url = self._resolve_url(*args)
        super(_BaseActions, self).go_to(resolved_url)
        return self

    def _generic_make_browser(self, webdriver_type, desired_cap_type, remote_url, desired_caps):
        """Override Selenium2Library's _generic_make_browser to allow for extra params
        to driver constructor."""
        kwargs = {}
        if not remote_url:
            if 'service_args' in inspect.getargspec(webdriver_type.__init__).args:
                kwargs['service_args'] = self.service_args
            browser = webdriver_type(**kwargs)
        else:
            browser = self._create_remote_web_driver(desired_cap_type, remote_url, desired_caps)
        return browser

    def _make_browser(self, browser_name, desired_capabilities=None, profile_dir=None, remote=None):
        creation_func = self._get_browser_creation_function(browser_name)

        if not creation_func:
            raise ValueError(browser_name + " is not a supported browser.")

        browser = creation_func(remote, desired_capabilities, profile_dir)
        browser.set_speed(self._speed_in_secs)
        browser.set_script_timeout(self._timeout_in_secs)
        browser.implicitly_wait(self._implicit_wait_in_secs)
        return browser

    def open(self, *args):
        """
        Wrapper for Selenium2Library's open_browser() that calls resolve_url for url logic and self.browser.
        It also deletes cookies after opening the browser.

        :param *args: A list or dictionary of variables mapping to a page object's uri template. For example given a
        template like this::

                class MyPageObject(PageObject):
                    uri = "category/{category}"

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
            if self.sauce_screenresolution:
                caps["screenResolution"] = self.sauce_screenresolution

            try:
                self.open_browser(resolved_url, self.browser, remote_url=remote_url, desired_capabilities=caps)
            except (urllib2.HTTPError, WebDriverException, ValueError) as e:
                raise exceptions.SauceConnectionError("Unable to run Sauce job.\n%s\n"
                                                      "Sauce variables were:\n"
                                                      "sauce_platform: %s\n"
                                                      "sauce_browserversion: %s\n"
                                                      "sauce_device_orientation: %s\n"
                                                      "sauce_screenresolution: %s"

                                                      % (str(e), self.sauce_platform,
                                                        self.sauce_browserversion, self.sauce_device_orientation,
                                                        self.sauce_screenresolution)
                )

            self.session_id = self.get_current_browser().session_id
            self.log("session ID: %s" % self.session_id)

        else:
            self.open_browser(resolved_url, self.browser)

        self.log("PO_BROWSER: %s" % (str(self.get_current_browser())), is_console=False)

        return self

    def close(self):
        """
        Wrapper for Selenium2Library's close_browser.
        :returns: None
        """
        self.close_browser()
        return self
