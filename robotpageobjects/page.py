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
import decorator
from Selenium2Library import Selenium2Library

from sig import get_method_sig
from .context import Context
from . import exceptions
from .base import _ComponentsManagerMeta, not_keyword, robot_alias, _BaseActions, _Keywords, Override, _SelectorsManager, _ComponentsManager


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
        return decorator.decorator(_PageMeta._must_return, f)

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
                classdict[member_name] = _PageMeta.must_return(classdict[member_name])

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
        #super(Page, self).__init__(*args, **kwargs)
        for base in Page.__bases__:
            base.__init__(self)

        # If a name is not explicitly set with the name attribute,
        # get it from the class name.
        try:
            self.name
        except AttributeError:
            self.name = self._titleize(self.__class__.__name__)

        # Allow setting of uri_template or uri, but make them the same internally
        if hasattr(self, 'uri_template'):
            self.uri = self.uri_template

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
                    if not in_ld:
                        keywords += _Keywords.get_robot_aliases(name, self._underscore(self.name))
                    else:
                        keywords.append(name)
        return keywords

    def _attempt_screenshot(self):
            try:
                self.capture_page_screenshot()
            except Exception, e:
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
            # Try to take a screenshot. If it fails due to no browser being open,
            # just raise the original exception. A failed screenshot is just noise here.
            # QAR-47920

            # Hardcode capture_page_screenshot. This is because run_on_failure
            # is being set to "Nothing" (DCLT-659 and DCLT-726).
            # TODO: After DCLT-827 is addressed, we can use run_on_failure again.

            # Walling off nested try/except in separate method to simplify scope issues with nested
            # try/excepts. Mess with at your own risk.
            self._attempt_screenshot()

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
