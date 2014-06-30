import os
from nose.tools import raises
from mock import patch
from robot.libraries.BuiltIn import BuiltIn
from unittest import skipUnless

import selenium

from basetestcase import BaseTestCase
from robotpageobjects import exceptions
from robotpageobjects.page import Page, Override, not_keyword, SelectorsDict
from robotpageobjects.optionhandler import OptionHandler


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


class OptionHandlerTestCase(BaseTestCase):
    def test_is_singleton(self):
        ids = []
        for i in range(3):
            ids.append(id(OptionHandler()))
        self.assertTrue(all(x == ids[0] for x in ids), "All OptionHandler instances should refer to the same instance")

    def test_no_robot_get_env_var(self):
        os.environ["PO_FOO"] = "bar"
        handler = OptionHandler()
        self.assertEquals(handler.get("foo"), "bar")

    def test_no_robot_env_not_set_is_none(self):
        handler = OptionHandler()
        self.assertIsNone(handler.get("fasdfasdfasdfsadf"))

    @skipUnless(os.name == "posix", "Skipping Windows, since environment variables are not case sensitive")
    def test_no_robot_ignore_lowercase_env_vars(self):
        os.environ["PO_BROWSEr"] = "firefox"
        handler = OptionHandler()
        self.assertIsNone(handler.get("browser"), "Mixed case environment variables should not be set")

    @raises(exceptions.VarFileImportErrorError)
    def test_var_file_import_exception(self):
        os.environ["PO_VAR_FILE"] = "foo/bar/asdfsadf/asdf"
        handler = OptionHandler()
        handler.get("PO_VAR_FILE")

    def test_no_robot_var_file(self):
        os.environ["PO_VAR_FILE"] = "%s/vars.py" % self.test_dir
        handler = OptionHandler()
        self.assertEquals(handler.get("author"), "Dickens")
        self.assertEquals(handler.get("dynamic"), "Python")

    @patch.object(BuiltIn, "get_variables")
    def test_robot(self, mock_get_variables):
        mock_get_variables.return_value = {"${browser}": "foobar"}
        handler = OptionHandler()
        self.assertEquals(handler.get("browser"), "foobar")


class ResolveUrlTestCase(BaseTestCase):
    def setUp(self):
        super(ResolveUrlTestCase, self).setUp()

        class PO(Page):
            pass

        self.PO = PO

    ### Exceptions ###
    @raises(exceptions.NoBaseUrlError)
    def test_no_baseurl_set_no_uri_attr_set_should_raise_NoBaseUrlException(self):
        self.PO()._resolve_url()

    @raises(exceptions.NoBaseUrlError)
    def test_no_baseurl_set_no_uri_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO()._resolve_url("bar")

    @raises(exceptions.NoBaseUrlError)
    def test_no_baseurl_set_uri_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO.uri = "/foo"
        self.PO()._resolve_url("bar")

    @raises(exceptions.NoUriAttributeError)
    def test_baseurl_set_no_uri_attr_set_should_raise_NoUriAttributeException(self):
        self.set_baseurl_env()
        self.PO()._resolve_url()

    @raises(exceptions.AbsoluteUriAttributeError)
    def test_baseurl_set_abs_uri_attr_should_raise_AbsoulteUrlAttributeException(self):
        self.set_baseurl_env()
        self.PO.uri = "http://www.example.com"
        self.PO()._resolve_url()

    @raises(exceptions.AbsoluteUriTemplateError)
    def test_baseurl_set_abs_uri_template_should_raise_AbsoluteUriTemplateException(self):
        self.set_baseurl_env()
        self.PO.uri_template = "http://www.ncbi.nlm.nih.gov/pubmed/{pid}"
        self.PO()._resolve_url({"pid": "123"})

    @raises(exceptions.InvalidUriTemplateVariableError)
    def test_baseurl_set_bad_vars_passed_to_uri_template(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        self.PO()._resolve_url({"foo": "bar"})

    @raises(exceptions.MissingSauceOptionError)
    def test_missing_sauce_apikey_should_raise_missing_sauce_option_error(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        os.environ["PO_SAUCE_USERNAME"] = "abc"
        self.PO.uri = "/foo"
        self.PO()

    @raises(exceptions.MissingSauceOptionError)
    def test_missing_sauce_username_should_raise_missing_sauce_option_error(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
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

    @skipUnless(BaseTestCase.are_sauce_creds_set_for_testing(), "SAUCE_USERNAME and SAUCE_APIKEY env vars must be set to test")
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

    ### Normative Cases ###
    def test_rel_uri_attr_set(self):
        self.set_baseurl_env()
        self.PO.uri = "/foo"
        po_inst = self.PO()
        url = po_inst._resolve_url()
        self.assertEquals(url, po_inst.baseurl + po_inst.uri)
        self.assertRegexpMatches(url, "file:///.+/foo$")

    def test_uri_vars_set(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        p = self.PO()
        url = p._resolve_url({"pid": "123"})
        pid = p.uri_vars["pid"]
        self.assertEquals("123", pid)
        self.assertEquals("http://www.ncbi.nlm.nih.gov/pubmed/123", url)

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
        self.assertEqual(selectors.get("baz"), "baz", "Selector 'baz' should be overridden in FooBarPage." )

    def test_page_resolve_selectors(self):
        class Foo(Page):
            selectors = {"foo": "xpath=id('display_settings_menu')//label[text() = '%s']"}

        foo = Foo()
        resolved = Foo().resolve_selector("foo", "bar")
        expected = "xpath=id('display_settings_menu')//label[text() = 'bar']"
        self.assertEqual(resolved, expected,
                         "Page.resolve_selector should resolve selectors with wildcards. Result was %s, but expected \"%s\"." % (resolved, expected))

    def test_selectors_resolve_selectors(self):
        selectors = SelectorsDict()
        selectors.merge({"foo": "xpath=id('display_settings_menu')//label[text() = '%s']"})

        resolved = selectors.resolve("foo", "bar")
        expected = "xpath=id('display_settings_menu')//label[text() = 'bar']"
        self.assertEqual(resolved, expected,
                         "SelectorsDict.resolve should resolve selectors with wildcards. Result was %s, but expected \"%s\"." % (resolved, expected))


class KeywordBehaviorTestCase(BaseTestCase):

    def setUp(self):

        super(KeywordBehaviorTestCase, self).setUp()
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


