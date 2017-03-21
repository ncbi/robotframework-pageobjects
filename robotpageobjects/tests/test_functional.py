import json
import os
import re
import unittest
import requests
import xml.etree.ElementTree as ET

from nose.tools import raises
from robotpageobjects import Page, exceptions
from robotpageobjects.tests.scenarios.po.result_component import ResultPage, ResultPageWithDOMStrategyLocator, HomePage, \
    HomePageWithDOMAdvancedToggler, TwoComponentsPage, ParaComponent, TwoComponentsSubPage
from robotpageobjects.tests.scenarios.po.loggingpage import LoggingPage
from robotpageobjects.tests.basetestcase import BaseTestCase


class SmokeTestCase(BaseTestCase):
    """
    Tests for basic options and option handling.

    For tests outside of Robot, individual environment variables
    in the form of "$PO_" (eg. $PO_BROWSER) set options.
    A variable of $PO_VAR_FILE can be set to a path to a Python
    module that can set variables as well. Individual
    environment variables override those set in the variable file.

    For tests within the Robot context the behavior follows
    standard Robot Framework..variables can be set on the
    command-line with --variable (eg. --variable=browser=firefox, which
    override the variables set in a variable file, set with --variablefile=

    The BaseTestCase setUp removes all PO environment variables.
    tearDown restores them. It also removes po_log file in
    setUp and tearDown and screenshots in setUp

    This assures that at the beginning of each test there are no
    PO_ environment variables set and that we are running with
    default options. The tests are then free to set environment variables or
    write variable files as needed.

    This test case tests browser option, but in effect also tests option handling, assuming
    that options are gotten internally using the optionhandler.OptionHandler class.
    """

    def test_unittest_rel_uri_set(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_rel_uri_attr.py")
        self.assert_run(run, search_output="OK", expected_browser="phantomjs")

    def test_robot_rel_uri_set(self):
        run = self.run_scenario("test_rel_uri_attr.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, search_output="PASS", expected_browser="phantomjs")

    def test_robot_no_name_attr_should_use_underscored_class_name_to_namespaced_keyword(self):
        run = self.run_scenario("test_rel_uri_attr_no_name_attr.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, search_output="PASS", expected_browser="phantomjs")

    def test_unittest_uri_template(self):
        # This tests open() as well as uri_template.
        self.set_baseurl_env()
        run = self.run_scenario("test_template_passed.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_robot_uri_template(self):
        # This tests open() as well as uri_template.
        run = self.run_scenario("test_template_passed.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_no_baseurl_gives_readable_error_in_robot(self):
        run = self.run_scenario("test_template_passed.robot")
        self.assert_run(run, expected_returncode=1, search_output="must set a baseurl")

    def stack_trace_in_robot_log(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_stack_trace.robot", v="baseurl:%s" % self.base_file_url, L="TRACE")
        self.assert_run(run, expected_returncode=1, search_output_xml="in raise_division_by_zero")

    def test_no_screenshot_attempt_on_initializing_page_with_component(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_page_with_component.robot")
        self.assert_run(run, expected_returncode=0, search_output="PASS",
                        not_in_output="Capture Page Screenshot")



class SauceTestCase(BaseTestCase):
    """
    Sauce exception tests are in the unit tests, not the
    functional tests.
    """

    def get_job_data(self, sid):
        username, apikey = self.get_sauce_creds()
        rest_url = "https://%s:%s@saucelabs.com/rest/v1/%s/jobs/%s" % (username, apikey, username, sid)
        resp = requests.get(rest_url)
        return json.loads(resp.content)

    def get_sid_from_log(self, is_robot=False):
        log_path = self.get_log_path(is_robot)
        try:
            f = open(log_path)
            content = f.read()
            try:
                return re.search(r"session ID: (.{32})", content).group(1)
            except (AttributeError, IndexError):
                raise Exception("Couldn't get the session ID from the log %s" % log_path)

        except OSError:
            raise "Couldn't find a log file at %s" % log_path
        except IOError:
            raise Exception("Couldn't open log file %s" % log_path)
        finally:
            f.close()

    @unittest.skipUnless(BaseTestCase.are_sauce_creds_set_for_testing(),
                         "Must set 'SAUCE_USERNAME' and 'SAUCE_APIKEY' ("
                         "not PO_SAUCE."
                         ".) "
                         "as an env "
                         "variables to run this test")
    def test_sauce_unittest(self):
        self.assertFalse(os.path.exists(self.get_log_path()))
        run = self.run_scenario("test_sauce.py")
        job_data = self.get_job_data(self.get_sid_from_log())

        # Just check an arbitrary entry in the job data returned from sauce.
        self.assertEquals(job_data["browser"], "firefox", "The job ran in Sauce")

        # We expect this to fail, because the test makes a purposely false assertion
        # to test that we can assert against things going on in Sauce.
        self.assert_run(run, expected_returncode=1, search_output="Title should have been 'foo' but was 'Home - "
                                                                  "PubMed - NCBI")

    @unittest.skipUnless(BaseTestCase.are_sauce_creds_set_for_testing(),
                         "Must set 'SAUCE_USERNAME' and 'SAUCE_APIKEY' ("
                         "not "
                         "PO_SAUCE..) "
                         "as an env "
                         "variables to run this test")
    def test_sauce_robot(self):
        self.assertFalse(os.path.exists(self.get_log_path(is_robot=True)))
        run = self.run_scenario("test_sauce.robot", variablefile=os.path.join(self.test_dir, "sauce_vars.py"))

        job_data = self.get_job_data(self.get_sid_from_log(is_robot=True))

        # Just check an arbitrary entry in the job data returned from sauce.
        self.assertEquals(job_data["browser"], "firefox", "The job ran in Sauce")
        self.assert_run(run, expected_returncode=1, search_output="Title should have been 'foo' but was 'Home - "
                                                                  "PubMed - NCBI")


class ActionsTestCase(BaseTestCase):
    """
    DCLT-768: TODO
    @unittest.skip("NOT IMPLEMENTED YET. ")
    def test_unittest_screenshot_on_failure(self):
        self.assert_screen_shots(0)
        self.run_scenario("test_fail.py")
        self.assert_screen_shots(1)
    """

    def test_robot_screen_shot_on_page_object_keyword_failure(self):
        self.assert_screen_shots(0)
        self.run_scenario("test_fail.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_screen_shots(1)

    def test_robot_screen_shot_on_se2lib_keyword_failure(self):
        self.assert_screen_shots(0)
        self.run_scenario("test_fail_se2lib_keyword.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_screen_shots(1)

    def test_manual_screenshot_outside_robot(self):
        self.assert_screen_shots(0)
        self.set_baseurl_env()
        run = self.run_scenario("test_manual_screen_shot.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")
        self.assert_screen_shots(1)

    def test_manual_screenshot_robot(self):
        self.assert_screen_shots(0)
        run = self.run_scenario("test_manual_screen_shot.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")
        self.assert_screen_shots(1)

    def test_go_to_robot(self):
        run = self.run_scenario("test_go_to.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_go_to_outside_robot(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_go_to.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_is_visible(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_is_visible.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_location_should_be_for_relative_path(self):
        run = self.run_scenario("test_location_should_be_for_relative_path.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_location_should_be_for_absolute_path(self):
        run = self.run_scenario("test_location_should_be_for_absolute_path.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

class SelectorsTestCase(BaseTestCase):
    def setUp(self):
        super(SelectorsTestCase, self).setUp()
        self.set_baseurl_env()

    def test_s2l_keyword_with_selector(self):
        run = self.run_scenario("test_s2l_keyword_with_selector.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_find_elements_with_selector(self):
        run = self.run_scenario("test_find_elements_with_selector.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_bad_selector_raises_exception(self):
        run = self.run_scenario("test_bad_selector.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_no_selector_raises_exception(self):
        run = self.run_scenario("test_no_selector.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_selector_template(self):
        run = self.run_scenario("test_templated_selector.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_selector_self_ref(self):
        run = self.run_scenario("test_selector_self_ref.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_no_robot_action_failing_should_not_warn_about_screenshot(self):
        run = self.run_scenario("test_fail.py")
        self.assertFalse("warn" in run.output.lower(), "No warning should be issued when a method fails outside "
                                                       "robot")

    def robot_importing_se2lib_after_page_object_should_work(self):
        # This run is duplicated, but it shows that SE2Lib library imported
        # with page objects works.
        run = self.run_scenario("test_template_passed.robot")
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def robot_importing_se2lib_before_page_object_should_work(self):
        run = self.run_scenario("test_se2lib_imported_before_po.robot")
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_selector_with_se2lib_keyword(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_selector_with_se2lib_keyword.robot")
        self.assert_run(run, expected_returncode=0, search_output="PASS")


class ComponentTestCase(BaseTestCase):
    def setUp(self):
        super(ComponentTestCase, self).setUp()
        self.set_baseurl_env()
        self.result_page_with_str_locator = ResultPage()
        self.result_page_with_dom_strategy_locator = ResultPageWithDOMStrategyLocator()
        self.homepage = HomePage()
        self.homepage_with_dom_toggler = HomePageWithDOMAdvancedToggler()
        self.two_comp_page = TwoComponentsPage()


    def test_selenium_implicit_wait_not_reset_within_component(self):
        self.result_page_with_str_locator.open()

        self.assertEquals(
            self.result_page_with_str_locator.get_selenium_implicit_wait(),
            "10 seconds"
        )

        self.assertEquals(
            self.result_page_with_str_locator.result.get_selenium_implicit_wait(),
            "10 seconds"
        )

    def test_get_instance_and_instances(self):
        # Test get_instance and get_instances in same test. get_instance()
        # get_instances() are called by the component admin class to set
        # component instances on the page object.
        # In the same component admin, get_instance and get_instances
        # are called so we can access the result, or results object(s).
        # You'd use get_instance() if you expected only one
        # instance, and get_instances() if you expected > 1.
        # Normally, of course, in the admin class, you'd call only
        # one of these, not both.
        self.result_page_with_str_locator.open()
        self.assertNotEquals(type(self.result_page_with_str_locator.result), list)

        # Should get the first result since we are accessing "result", not "results".
        self.assertEquals(self.result_page_with_str_locator.result.price, "$14.00")

        # Now access "results" in the plural.
        self.assertEquals(len(self.result_page_with_str_locator.results), 3)
        self.assertEquals(self.result_page_with_str_locator.results[0].price, "$14.00")

    def test_locator_as_dom(self):
        self.result_page_with_dom_strategy_locator.open()
        results = self.result_page_with_dom_strategy_locator.results

        # The locator uses DOM strategy to get the nodes via a call
        # to execute_javascript() and limits to 2 results, just
        # to make sure we are testing the right thing.
        self.assertEquals(len(results), 2)
        # Check that the result object works.
        self.assertEquals(results[0].price, "$14.00")

    def test_component_inside_component(self):
        # A component should be able to contain other components. You'd access
        # sub component by accessing the sub component name as a property on the
        # parent component.

        # These tests import the page classes directly, instead of going
        # through run_scenario(), which is inconsistent with the rest of the
        # Python tests. We do this because it's just clearer and easier to
        # debug. We should probably clean up the other tests to do the same.
        # See QAR-47882.

        # We don't see the need for writing these tests in both Robot and Python
        # because we already feel confident that page objects perform the same
        # in both contexts, as the other tests show.
        self.homepage.open()
        search_component = self.homepage.search

        self.homepage.textfield_value_should_be("id=q", "", "The search component's input doesn't start blank")
        search_component.set_search_term("foo")
        self.homepage.textfield_value_should_be("id=q", "foo", "Search component can't set a search value")

        # Access a sub component
        advanced_option_toggler_component = search_component.advancedoptiontoggler

        self.homepage.element_should_not_be_visible("id=advanced-search-content")
        advanced_option_toggler_component.open()
        self.homepage.element_should_be_visible("id=advanced-search-content")

    def test_component_inside_component_with_dom(self):
        # When you have a component inside another component, the parent should be
        # able to search for the child using the child's locator. The child's locator
        # should be interpreted with reference to the parent's reference_webelement.

        self.homepage_with_dom_toggler.open()
        search_component = self.homepage_with_dom_toggler.searchcomponentwithdomadvancedtoggler
        advanced_option_toggler_component = search_component.advancedoptiontoggler

    def test_use_selectors_to_get_non_child_element(self):
        self.homepage.open()
        toggler = self.homepage.search.advancedoptiontoggler
        toggler.open()
        self.assertEquals(toggler.advanced_text, "These are advanced options")

    def test_page_inherits_from_multiple_components(self):
        paras = self.two_comp_page.open().paras
        self.assertTrue(len(paras) > 1, "Locator for body component is being used, so not finding "
                                        "more than one paragraph component on page")
    def test_calling_log_from_component(self):
        self.homepage.open()

        attr_err_raised = False
        try:
            self.homepage.get_some_property()
        except AttributeError:
            attr_err_raised = True

        self.assertFalse(attr_err_raised, "AttributeError raised when trying to call log() from a component")

    def test_page_inherits_super_pages_components(self):
        self.two_comp_page = TwoComponentsSubPage().open()
        try:
            body = self.two_comp_page.body
            found = True
        except AttributeError:
            found = False
        self.assertTrue(found, "body attribute should exist when inheriting from super class")

    def test_page_overrides_super_pages_components(self):
        self.two_comp_page = TwoComponentsSubPage().open()
        paras = self.two_comp_page.paras
        self.assertEqual(len(paras), 1, "Overridden locator for paras should return just the last one")

    def test_page_override_without_override_class_raises_warning(self):
        run = self.run_scenario("test_page_override_without_override_class.py", env={"PYTHONPATH": self.po_dir})
        self.assert_run(run, expected_returncode=0, search_output="KeyOverrideWarning")

    def tearDown(self):
        super(ComponentTestCase, self).tearDown()
        self.result_page_with_str_locator.close()
        self.result_page_with_dom_strategy_locator.close()
        self.homepage.close()
        self.two_comp_page.close()


class KeywordsTestCase(BaseTestCase):
    def test_dont_have_to_specify_page_name_in_keyword_when_2_page_objects_inherit_it(self):
        run = self.run_scenario("test_dont_have_to_specify_page_name_in_keyword_when_2_page_objects_inherit_it.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_dont_have_to_specify_page_name_for_keyword_when_2_page_objects_define_it(self):
        run = self.run_scenario("test_dont_have_to_specify_page_name_for_keyword_when_2_page_objects_define_it.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_dont_have_to_specify_page_name_when_extending_se2lib_keyword(self):
        run = self.run_scenario("test_dont_have_to_specify_page_name_when_extending_se2lib_keyword.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_keyword_does_not_return_page_object(self):
        run = self.run_scenario("test_does_not_return.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=1,
                        search_output="You must return either a page object or an appropriate value from the page object method")

    def test_can_alias_without_page_name(self):
        run = self.run_scenario("test_can_call_aliased_method_without_page_name.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_can_alias_with_page_name(self):
        run = self.run_scenario("test_can_call_aliased_method_with_page_name.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_can_call_unaliased_with_page_name(self):
        run = self.run_scenario("test_can_call_unaliased_method_with_page_name.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_negative_index_in_table_keywords(self):
        run = self.run_scenario("test_negative_index_in_table_keywords.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_se2lib_keywords_are_still_available_if_both_se2lib_and_po_are_imported(self):
        run = self.run_scenario("test_se2lib_called_before_po.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

class WaitingTestCase(BaseTestCase):
    def test_implicit_wait_default_works(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_implicit_se_wait.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_implicit_wait_fails_with_option_set_to_1(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_implicit_se_wait.py", env={"PO_SELENIUM_IMPLICIT_WAIT": "1"})
        self.assert_run(run, expected_returncode=1, search_output="FAIL")

    def test_implicit_wait_can_be_set_to_0(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_implicit_se_wait_0.py", env={"PO_SELENIUM_IMPLICIT_WAIT": "0"})
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_can_set_wait_on_call_to_find_element_and_find_elements(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_pass_explicit_wait_to_find_element.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_wait_till_element_disappears(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_wait_until_not_visible.py")
        self.assert_run(run, expected_returncode=0)


class LoggingTestCase(BaseTestCase):
    """
    # Tests that assert whether or not messages are logged depending on the log level
    # logged in relation to the log level threshold.

    # For example, given these logging levels (from severe to less severe):

    CRITICAL
    ERROR
    WARNING
    INFO
    DEBUG
    NOTSET

    Let's say that the threshold is set at INFO, and we log "above" the threshold at
    CRITICAL by calling

    self.log("hello world", "CRITICAL")

    We expect that this message would get logged.

    If, on the other hand, we logged below
    the threshold at "DEBUG", we'd expect the message to not get logged.
    """

    def test_log_below_threshold_should_log_to_stdout_but_not_to_file_robot(self):
        # Unless we specify is_console=False, we always log to stdout in Robot
        run = self.run_scenario("test_log_below_threshold.robot")
        self.assert_run(run, expected_returncode=0, search_output="DEBUG - Logging Page - hello world",
                        not_in_log="hello world")

    def test_log_below_threshold_should_not_log_to_stdout_and_not_to_file_if_is_console_false_robot(self):
        # Unless we specify is_console=False, we always log to stdout in Robot
        run = self.run_scenario("test_log_below_threshold_is_console_false.robot")
        self.assert_run(run, expected_returncode=0, not_in_output="hello world", not_in_log="hello world")

    def test_log_below_threshold_should_not_log_to_stdout_and_file_python(self):
        run = self.run_scenario("test_log_below_threshold.py")
        self.assert_run(run, expected_returncode=0, not_in_output="hello world", not_in_log="hello world")

    def test_log_below_threshold_is_console_false_should_not_log_to_file_and_not_to_console_python(self):
        run = self.run_scenario("test_log_below_threshold_is_console_false.py")
        self.assert_run(run, expected_returncode=0, not_in_output="hello world", not_in_log="hello world")

    def test_log_above_threshold_should_log_to_stdout_and_file_robot(self):
        run = self.run_scenario("test_log_above_threshold.robot")
        self.assert_run(run, expected_returncode=0, search_output="WARNING - Logging Page - hello world",
                        search_log="hello world")

    def test_log_at_threshold_should_log_to_stdout_and_file_robot(self):
        run = self.run_scenario("test_log_at_threshold.robot")
        self.assert_run(run, expected_returncode=0, search_output="INFO - Logging Page - hello world",
                        search_log="hello world")

    def test_log_at_or_above_threshold_should_log_to_stdout_and_file_python(self):
        run = self.run_scenario("test_log_at_threshold.py")
        self.assert_run(run, expected_returncode=0, search_output="INFO - Logging Page - hello world",
                        search_log="INFO - Logging Page - hello world")

    def test_log_at_or_above_threshold_console_false_should_log_to_file_but_not_stdout_python(self):
        run = self.run_scenario("test_log_at_threshold_is_console_false.py")
        self.assert_run(run, expected_returncode=0, not_in_output="hello world", search_log="INFO - Logging Page - hello world")

    def test_one_instance_of_file_logger(self):

        class MyPage(Page):
            pass

        path_to_log = os.path.join(os.getcwd(), "po_log.txt")

        # Clear the log in case any other test has written to it. Set up deals with
        # po_log.txt at tests/scenarios directory.
        f = open(path_to_log, "w")
        f.write("")
        f.close()

        # Now log from two different page objects
        Page().log("hello", is_console=False)
        MyPage().log("world", is_console=False)
        f = open(path_to_log)
        log_content =  f.read()
        try:
            # We expect to see two lines in the log, logged in order from Page to My Page.
            self.assertRegexpMatches(log_content, r".+ - INFO - Page - hello\n.+ - INFO - My Page - world$")

            # 3 lines are really 2 lines because of final line break
            self.assertEquals(len(log_content.split("\n")), 3)

        finally:
            f.close()


            os.unlink(path_to_log)

    def test_log_non_string(self):
        try:
            Page().log([1,2,3], is_console=False)
        except TypeError:
            self.fail("Logging a non string causes a TypeError")

    @raises(ValueError)
    def test_log_at_invalid_level_python(self):
        LoggingPage().log_invalid()

class LibdocTestCase(BaseTestCase):

    def test_gen_doc(self):
        # generate libdoc xml
        outxml = 'libdoc.xml'
        run = self.run_program("python", ".", "robotpageobjects.page.Page %s" % outxml, **{"m": "robot.libdoc"})
        self.assert_run(run, expected_returncode=0, search_output=outxml)

        root = ET.parse(outxml).getroot()
        kwentry = root.findall(".//kw[@name='Log']")
        if len(kwentry) == 0:
            raise AssertionError('Expected to find entry for "Log" in %s' % outxml)
        kwentry = kwentry[0]
        kwargs = kwentry.findall('./arguments/arg')
        if len(kwargs) != 3:
            raise AssertionError('Expected to find 3 arguments for "Log" in %s' % outxml)
        doc = kwentry.findall('./doc')[0]
        if 'DEBUG' not in doc.text:
            raise AssertionError('Expected to find "DEBUG" in docmentation for "Log" in %s' % outxml)

class MultipleSuiteLibraryImport(BaseTestCase):

    def test_libraries_stay_imported(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_s2l_imported_multiple_a.robot test_s2l_imported_multiple_b.robot")
        self.assert_run(run, expected_returncode=0)
