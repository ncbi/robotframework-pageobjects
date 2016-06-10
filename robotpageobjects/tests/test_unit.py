import inspect
import os
import sys
from nose.tools import raises
from mock import patch
from robot.libraries.BuiltIn import BuiltIn
from unittest import skipUnless
import selenium
from selenium import webdriver

from robotpageobjects.tests.basetestcase import BaseTestCase
from robotpageobjects import exceptions
from robotpageobjects.page import Page, _Keywords, Override, not_keyword
from robotpageobjects.optionhandler import OptionHandler

test_dir = os.path.dirname(os.path.realpath(__file__))
scenario_dir = os.path.join(test_dir, "scenarios")
po_dir = os.path.join(scenario_dir, "po")
sys.path.append(po_dir)

from basepageobjects import BaseHomePage, BaseResultsPage


class InheritFromSe2LibTestCase(BaseTestCase):
    def setUp(self):
        super(InheritFromSe2LibTestCase, self).setUp()

        class PO(Page):
            pass

        self.po = PO()

    def test_no_robot_se2lib_exposed(self):
        # We can't test this as a unittest in
        # robot, so see functional test class.

        try:
            getattr(self.po, "title_should_be")
        except AttributeError:
            self.fail("SE2Lib methods are not exposed as direct page object attributes")

class MockPage(object):
        pass

class OptionHandlerTestCase(BaseTestCase):

    path_to_var_file = os.path.join(BaseTestCase.test_dir, "vars.py")

    def test_is_singleton(self):
        ids = []
        for i in range(3):
            ids.append(id(OptionHandler(MockPage())))
        self.assertTrue(all(x == ids[0] for x in ids), "All OptionHandler instances should refer to the same instance")

    def test_no_robot_get_env_var(self):
        os.environ["PO_FOO"] = "bar"
        handler = OptionHandler(MockPage())
        self.assertEquals(handler.get("foo"), "bar")

    def test_no_robot_env_not_set_is_none(self):
        handler = OptionHandler(MockPage())
        self.assertIsNone(handler.get("fasdfasdfasdfsadf"))

    @skipUnless(os.name == "posix", "Skipping Windows, since environment variables are not case sensitive")
    def test_no_robot_ignore_lowercase_env_vars(self):
        os.environ["PO_BROWSEr"] = "firefox"
        handler = OptionHandler(MockPage())
        self.assertIsNone(handler.get("browser"), "Mixed case environment variables should not be set")

    @raises(exceptions.VarFileImportErrorError)
    def test_var_file_import_exception(self):
        os.environ["PO_VAR_FILE"] = "foo/bar/asdfsadf/asdf"
        handler = OptionHandler(MockPage())
        handler.get("PO_VAR_FILE")

    def test_no_robot_var_file(self):
        os.environ["PO_VAR_FILE"] = self.path_to_var_file
        handler = OptionHandler(MockPage())
        self.assertEquals(handler.get("author"), "Dickens")
        self.assertEquals(handler.get("dynamic"), "Python")

    @patch.object(BuiltIn, "get_variables")
    def test_robot(self, mock_get_variables):
        mock_get_variables.return_value = {"${browser}": "foobar"}
        handler = OptionHandler(MockPage())
        self.assertEquals(handler.get("browser"), "foobar")

    @patch.object(BuiltIn, "get_variables")
    def test_robot_can_get_vars_from_env(self, mock_get_variables):
        os.environ["PO_BROWSER"] = "opera"
        try:
            handler = OptionHandler(MockPage())
            self.assertEquals(handler.get("browser"), "opera")
        except Exception as e:
            raise e
        finally:
            del os.environ["PO_BROWSER"]

    @patch.object(BuiltIn, "get_variables")
    def test_robot_env_overrides_var_file(self, mock_get_variables):
        os.environ["PO_AUTHOR"] = "Twain"
        os.environ["PO_VAR_FILE"] = self.path_to_var_file
        try:
            handler = OptionHandler(MockPage())
            self.assertEquals(handler.get("author"), "Twain")
        except Exception as e:
            raise e
        finally:
            del os.environ["PO_AUTHOR"]
            del os.environ["PO_VAR_FILE"]

    @patch.object(BuiltIn, "get_variables")
    def test_robot_cmd_line_var_overrides_env_var(self, mock_get_variables):
        os.environ["PO_BROWSER"] = "firefox"
        mock_get_variables.return_value = {"${browser}": "chrome"}
        try:
            handler = OptionHandler(MockPage())
            self.assertEquals(handler.get("browser"), "chrome")
        except Exception as e:
            raise e
        finally:
            del os.environ["PO_BROWSER"]

    @patch.object(BuiltIn, "get_variables")
    def test_robot_cmd_line_var_overrides_var_file(self, mock_get_variables):
        mock_get_variables.return_value = {"${author}": "Twain"}
        os.environ["PO_VAR_FILE"] = self.path_to_var_file
        try:
            handler = OptionHandler(MockPage())
            self.assertEquals(handler.get("author"), "Twain")
        except Exception as e:
            raise e
        finally:
            del os.environ["PO_VAR_FILE"]

    def test_get_options_from_page_object(self):
        p = MockPage()
        p.options = {'author': 'Twain'}
        handler = OptionHandler(p)
        self.assertEquals(handler.get("author"), "Twain")


class SauceTestCase(BaseTestCase):
    def setUp(self):
        super(SauceTestCase, self).setUp()

        class PO(Page):
            pass

        self.PO = PO

    @raises(exceptions.MissingSauceOptionError)
    def test_missing_sauce_apikey_should_raise_missing_sauce_option_error(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        os.environ["PO_SAUCE_PLATFORM"] = "Windows 8.1"
        os.environ["PO_SAUCE_USERNAME"] = "abc"
        self.PO.uri = "/foo"
        self.PO()

    @raises(exceptions.MissingSauceOptionError)
    def test_missing_sauce_username_should_raise_missing_sauce_option_error(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        os.environ["PO_SAUCE_PLATFORM"] = "Windows 8.1"
        os.environ["PO_SAUCE_APIKEY"] = "abc"
        self.PO.uri = "/foo"
        self.PO()

    @raises(exceptions.MissingSauceOptionError)
    def test_missing_sauce_platform_should_raise_missing_sauce_option_error(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        os.environ["PO_BROWSER"] = "Firefox"
        os.environ["PO_SAUCE_BROWSERVERSION"] = "37"
        os.environ["PO_SAUCE_USERNAME"] = "abc"
        os.environ["PO_SAUCE_APIKEY"] = "abc"
        self.PO.uri = "/foo"
        self.PO()

    @raises(exceptions.SauceConnectionError)
    def test_sauce_connection_error(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        os.environ["PO_BROWSER"] = "Firefox"
        os.environ["PO_SAUCE_BROWSERVERSION"] = "27"
        os.environ["PO_SAUCE_USERNAME"] = "foo"
        os.environ["PO_SAUCE_APIKEY"] = "bar"
        os.environ["PO_SAUCE_PLATFORM"] = "Windows 8.1"
        self.PO.uri = "/foo"
        p = self.PO()
        p.open()

    @skipUnless(BaseTestCase.are_sauce_creds_set_for_testing(),
                "SAUCE_USERNAME and SAUCE_APIKEY env vars must be set to test")
    @raises(selenium.common.exceptions.WebDriverException)
    def test_sauce_invalid_browser(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        os.environ["PO_BROWSER"] = "Firefox"
        os.environ["PO_SAUCE_BROWSERVERSION"] = "27"
        username, apikey = self.get_sauce_creds()
        os.environ["PO_SAUCE_USERNAME"] = username
        os.environ["PO_SAUCE_APIKEY"] = apikey
        os.environ["PO_SAUCE_PLATFORM"] = "Winows 8.1"
        self.PO.uri = "/foo"
        p = self.PO()
        p.open()


class ResolveUrlTestCase(BaseTestCase):
    def setUp(self):
        super(ResolveUrlTestCase, self).setUp()

        class PO(Page):
            pass

        self.PO = PO

    ### Exceptions ###
    @raises(exceptions.UriResolutionError)
    def test_no_baseurl_set_and_no_uri_attr_set(self):
        """No baseurl is set, and there is no "uri" set in the PO."""

        self.PO()._resolve_url()

    @raises(exceptions.UriResolutionError)
    def test_no_baseurl_set_and_no_uri_attr_set_and_uri_vars_set(self):
        """No baseurl is set, and there is no "uri" set in the PO,
        and a variable was passed in."""

        self.PO()._resolve_url("bar")

    @raises(exceptions.UriResolutionError)
    def test_no_baseurl_set_and_uri_attr_set_and_uri_vars_set(self):
        """No baseurl is set. A uri is set, but a variable was passed in."""

        self.PO.uri = "/foo"
        self.PO()._resolve_url("bar")

    @raises(exceptions.UriResolutionError)
    def test_baseurl_set_abs_uri_attr(self):
        """An absolute url (with scheme) was set as the uri."""

        self.set_baseurl_env()
        self.PO.uri = "http://www.example.com"
        self.PO()._resolve_url()

    @raises(exceptions.UriResolutionError)
    def test_baseurl_set_and_abs_uri_template(self):
        """An absolute uri template was set."""

        self.set_baseurl_env()
        self.PO.uri_template = "http://www.ncbi.nlm.nih.gov/pubmed/{pid}"
        self.PO()._resolve_url({"pid": "123"})

    @raises(exceptions.UriResolutionError)
    def test_bad_vars_passed_to_uri_template(self):
        """The variable names passed in do not match the template."""

        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        self.PO()._resolve_url({"foo": "bar"})

    @raises(exceptions.UriResolutionError)
    def test_too_many_vars_passed_to_uri_template_in_robot(self):
        self.set_baseurl_env()
        self.PO.uri_template = "/pubmed/{pid}"
        po = self.PO()
        po._is_robot = True
        po._resolve_url("pid=foo", "bar=baz")

    @raises(exceptions.UriResolutionError)
    def test_no_vars_passed_to_uri_template(self):
        """There is a template but no variables are possed in."""

        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        self.PO()._resolve_url()

    @raises(exceptions.UriResolutionError)
    def test_wrong_var_name_in_robot(self):
        self.set_baseurl_env()
        self.PO.uri_template = "/pubmed/{pid}"
        po = self.PO()
        po._is_robot = True
        po._resolve_url("foo=bar")

    @raises(exceptions.UriResolutionError)
    def test_names_not_provided_in_robot(self):
        self.set_baseurl_env()
        self.PO.uri_template = "/pubmed/{pid}"
        po = self.PO()
        po._is_robot = True
        po._resolve_url("1234")

    @raises(exceptions.UriResolutionError)
    def test_absolute_url_without_scheme(self):
        self.set_baseurl_env()
        self.PO.uri_template = "/pubmed/{pid}"
        po = self.PO()
        po._resolve_url("//www.google.com")

    ### Normative Cases ###
    def test_url_string_bypasses_uri_template(self):
        """A path was passed in as a string (inside or outside Robot). It should just be appended to
        the baseurl, even if there is a template in the PO."""
        self.set_baseurl_env()
        self.PO.uri_template = "/pubmed/{pid}"
        po = self.PO()
        path = "/pmc/1234"
        url = po._resolve_url(path)
        self.assertEquals(url, po.baseurl + path)

    def test_url_string_bypasses_uri(self):
        """A path was passed in as a string (inside or outside Robot). It should just be appended to
        the baseurl, even if there is a uri set in the PO."""
        self.set_baseurl_env()
        self.PO.uri = "/pubmed"
        po = self.PO()
        path = "/pmc/1234"
        url = po._resolve_url(path)
        self.assertEquals(url, po.baseurl + path)

    def test_absolute_url_bypasses_uri_template(self):
        """An absolute url was passed in as a string (inside or outside Robot). It should just be used instead of
        the PO's uri_template."""
        self.set_baseurl_env()
        self.PO.uri_template = "/pubmed/{pid}"
        po = self.PO()
        abs_url = "http://www.google.com"
        resolved_url = po._resolve_url(abs_url)
        self.assertEquals(resolved_url, abs_url)

    def test_absolute_url_bypasses_uri(self):
        """An absolute url was passed in as a string (inside or outside Robot). It should just be used instead of
        the PO's uri."""
        self.set_baseurl_env()
        self.PO.uri = "/pubmed/{pid}"
        po = self.PO()
        abs_url = "http://www.google.com"
        resolved_url = po._resolve_url(abs_url)
        self.assertEquals(resolved_url, abs_url)

    def test_rel_uri_is_resolved(self):
        self.set_baseurl_env()
        self.PO.uri = "/foo"
        po_inst = self.PO()
        url = po_inst._resolve_url()
        self.assertEquals(url, po_inst.baseurl + po_inst.uri)
        self.assertRegexpMatches(url, "file:///.+/foo$")

    def test_uri_template_is_resolved(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        p = self.PO()
        url = p._resolve_url({"pid": "123"})
        pid = p.uri_vars["pid"]
        self.assertEquals("123", pid)
        self.assertEquals("http://www.ncbi.nlm.nih.gov/pubmed/123", url)

    def test_baseurl_set_no_uri_attr_set(self):
        """A baseurl is set, but no variables were passed in and no "uri" was set."""

        self.set_baseurl_env()
        self.PO()._resolve_url()


class SelectorsTestCase(BaseTestCase):
    @raises(exceptions.DuplicateKeyError)
    def test_selectors_dup(self):
        class BaseFoo(object):
            selectors = {"foo": "foo"}

        class BaseBar(object):
            selectors = {"foo": "bar"}

        class FooBarPage(Page, BaseFoo, BaseBar):
            selectors = {"foo": "baz"}

        page = FooBarPage()

    def test_selectors_merge_override(self):
        class BaseFoo(object):
            selectors = {"foo": "foo"}

        class BaseBar(object):
            selectors = {"bar": "bar",
                         "baz": "cat"}

        class FooBarPage(Page, BaseFoo, BaseBar):
            selectors = {Override("baz"): "baz"}

        page = FooBarPage()
        selectors = page.selectors
        self.assertEqual(selectors.get("foo"), "foo", "Selectors should contain 'foo' from BaseFoo.")
        self.assertEqual(selectors.get("bar"), "bar", "Selectors should contain 'bar' from BaseBar.")
        self.assertEqual(selectors.get("baz"), "baz", "Selector 'baz' should be overridden in FooBarPage.")


class KeywordTestCase(BaseTestCase):

    def setUp(self):
        super(KeywordTestCase, self).setUp()
        # No need for testing in Robot too, since we will have a general test
        # that exceptions get raised properly, and this is just another exception.
        class P(Page):
            uri = ""

            def not_return_none(self):
                return True

            def return_none(self):
                pass

            @not_keyword
            def return_none_not_keyword(self):
                pass

            def _return_none(self):
                pass

        self.p = P()

    def test_method_not_return_none_should_not_raise_exception(self):
        self.assertTrue(self.p.not_return_none())

    @raises(exceptions.KeywordReturnsNoneError)
    def test_method_returning_none_should_raise_exception(self):
        self.p.return_none()

    def test_method_returning_none_with_not_keyword_should_not_raise_exception(self):
        self.assertIsNone(self.p.return_none_not_keyword())

    def test_private_method_returning_none_should_not_raise_exception(self):
        self.assertIsNone(self.p._return_none())

    def test_se2lib_keywords_fixed_to_mention_selectors(self):
        m = getattr(self.p, "click_element")
        docstring = inspect.getdoc(m)
        first_line_of_docstring = docstring.split("\n")[0]
        self.assertEquals(first_line_of_docstring, "click_element(self, selector_or_locator)")
        self.assertTrue("Click element identified by `selector` or `locator`" in docstring)

    def test_is_obj_keyword(self):
        is_obj_keyword = _Keywords.is_obj_keyword
        self.assertTrue(is_obj_keyword(Page.click_element))
        self.assertFalse(is_obj_keyword(Page.selectors))
        self.assertFalse(is_obj_keyword(Page._is_url_absolute))
        self.assertFalse(is_obj_keyword(Page.get_current_browser))
        self.assertFalse(is_obj_keyword(Page.driver))

    def test_is_obj_keyword_by_name(self):
        is_obj_keyword_by_name = _Keywords.is_obj_keyword_by_name
        self.assertTrue(is_obj_keyword_by_name("click_element", Page))
        self.assertFalse(is_obj_keyword_by_name("selectors", Page))
        self.assertFalse(is_obj_keyword_by_name("_is_url_absolute", Page))
        self.assertFalse(is_obj_keyword_by_name("get_current_browser", Page))
        self.assertFalse(is_obj_keyword_by_name("driver", Page))
        self.assertFalse(is_obj_keyword_by_name("foobarbatdaniel", Page))


    def test_page_property_raises_exception(self):

        class MyPage(Page):

            @property
            def some_property(self):
                raise Exception()

        exc_raised = False
        try:
            MyPage().get_keyword_names()
        except:
            exc_raised = True

        self.assertFalse(exc_raised, "An exception was raised when trying to access a page object property that "
                                     "raises an exception itself")


class LoggingLevelsTestCase(BaseTestCase):
    # Tests protected method Page._get_normalized_logging_levels, which given a
    # String logging level should return a tuple of the attempted string logging level
    # with the associated integer level from Python's logging module. This method
    # deals with the fact that Robot has different logging levels than python. It's called
    # by Page.log().

    def setUp(self):
        super(LoggingLevelsTestCase, self).setUp()
        self.normalize_fn = Page._abstracted_logger.get_normalized_logging_levels

    def test_log_CRITICAL_python(self):
        level_tup = self.normalize_fn("CRITICAL", False)
        self.assertEquals(level_tup, ("CRITICAL", 50))

    def test_log_CRITICAL_robot(self):
        level_tup = self.normalize_fn("CRITICAL", True)
        self.assertEquals(level_tup, ("WARN", 30))

    def test_log_WARN_python(self):
        level_tup = self.normalize_fn("WARN", False)
        self.assertEquals(level_tup, ("WARN", 30))

    def test_log_WARNING_python(self):
        level_tup = self.normalize_fn("WARNING", False)
        self.assertEquals(level_tup, ("WARNING", 30))

    def test_log_WARN_robot(self):
        level_tup = self.normalize_fn("WARN", True)
        self.assertEquals(level_tup, ("WARN", 30))

    def test_log_WARNING_robot(self):
        level_tup = self.normalize_fn("WARNING", True)
        self.assertEquals(level_tup, ("WARN", 30))

    def test_log_INFO_python(self):
        level_tup = self.normalize_fn("INFO", False)
        self.assertEquals(level_tup, ("INFO", 20))

    def test_log_INFO_robot(self):
        level_tup = self.normalize_fn("INFO", False)
        self.assertEquals(level_tup, ("INFO", 20))

    def test_log_DEBUG_python(self):
        level_tup = self.normalize_fn("DEBUG", False)
        self.assertEquals(level_tup, ("DEBUG", 10))

    def test_log_DEBUG_robot(self):
        level_tup = self.normalize_fn("DEBUG", True)
        self.assertEquals(level_tup, ("DEBUG", 10))

    def test_log_TRACE_python(self):
        level_tup = self.normalize_fn("TRACE", False)
        self.assertEquals(level_tup, ("NOTSET", 0))

    def test_log_TRACE_robot(self):
        level_tup = self.normalize_fn("TRACE", True)
        self.assertEquals(level_tup, ("TRACE", 0))

    def test_log_NOTSET_python(self):
        level_tup = self.normalize_fn("NOTSET", False)
        self.assertEquals(level_tup, ("NOTSET", 0))

    def test_log_NOTSET_robot(self):
        level_tup = self.normalize_fn("NOTSET", True)
        self.assertEquals(level_tup, ("TRACE", 0))

    @raises(ValueError)
    def test_log_invalid_log_level_should_raise_value_error_python(self):
        level_tup = self.normalize_fn("FOO", False)
        self.assertEquals(level_tup, ("FOO", 0))

    @raises(ValueError)
    def test_log_invalid_log_level_should_raise_value_error_robot(self):
        level_tup = self.normalize_fn("FOO", True)
        self.assertEquals(level_tup, ("FOO", 0))

    def test_log_valid_but_lowercase_level_python(self):
        level_tup = self.normalize_fn("inFo", False)
        self.assertEquals(level_tup, ("INFO", 20))


class SelectorTemplateTestCase(BaseTestCase):
    def setUp(self):
        super(SelectorTemplateTestCase, self).setUp()
        self.p = Page()
        self.p.selectors["foo"] = "xpath=//foo[{n}]/{el}"

    def test_basic(self):
        self.assertEquals("xpath=//foo[3]/p", self.p.resolve_selector("foo", n=3, el="p"))

    def test_too_many_args(self):
        self.assertEquals("xpath=//foo[3]/p", self.p.resolve_selector("foo", n=3, el="p", boo="bat"))

    @raises(exceptions.SelectorError)
    def test_not_enough_args(self):
        self.p.resolve_selector("foo", n=3)

    @raises
    def test_wrong_args(self):
        self.p.resolve_selector("foo", n=3, ep="p")


class GetSubclassFromPOModuleTestCase(BaseTestCase):
    def setUp(self):
        super(GetSubclassFromPOModuleTestCase, self).setUp()
        self.p = BaseHomePage()

    @raises(exceptions.PageSelectionError)
    def test_no_fallback_raises_exception_with_nonexistent_package(self):
        klass = self.p.get_subclass_from_po_module("nonexistentpageobjects", BaseResultsPage, fallback_to_super=False)

    def test_with_fallback_with_nonexistent_package(self):
        klass = self.p.get_subclass_from_po_module("nonexistentpageobjects", BaseResultsPage, fallback_to_super=True)
        self.assertEqual(klass, BaseResultsPage, "Fallback with nonexistent package should fall back to class"
                                                      "BaseSearchResultPage.")

    def test_package_on_path_with_fallback_succeeds(self):
        klass = self.p.get_subclass_from_po_module("mydbpageobjects", BaseResultsPage, fallback_to_super=True)
        self.assertEqual(klass.__name__, "MyDBResultsPage", "MyDBResultsPage class should be selected.")

    def test_package_on_path_without_fallback_succeeds(self):
        klass = self.p.get_subclass_from_po_module("mydbpageobjects", BaseResultsPage, fallback_to_super=False)
        self.assertEqual(klass.__name__, "MyDBResultsPage", "MyDBResultsPage class should be selected.")


class ServiceArgsTestCase(BaseTestCase):

    def test_set_service_args(self):
        class P(Page):pass

        os.environ["PO_SERVICE_ARGS"] = "--cookies-file=foo.txt"
        service_args = P().service_args
        self.assertTrue(isinstance(service_args, list), "Service args is a list")
        self.assertEquals(len(service_args), 1, "Service args property has 1 member")
        self.assertEquals(
            service_args[0],
            "--cookies-file=foo.txt",
            "Service args is what we set it to be"
        )
