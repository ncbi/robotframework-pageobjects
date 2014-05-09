import glob
import json
import os
import re
import unittest

import requests

from basetestcase import BaseTestCase
from robotpageobjects import Page, Component, ComponentManager, robot_alias
from robot.utils import asserts


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


class SauceTestCase(BaseTestCase):

    """
    Sauce exception tests are in the unit tests, not the
    functional tests.
    """

    def get_job_data(self, sid):
        username, apikey = self.get_sauce_creds()
        rest_url = "https://%s:%s@saucelabs.com/rest/v1/%s/jobs/%s" %(username, apikey, username, sid)
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

    @unittest.skipUnless(BaseTestCase.are_sauce_creds_set_for_testing(), "Must set 'SAUCE_USERNAME' and 'SAUCE_APIKEY' ("
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

    @unittest.skipUnless(BaseTestCase.are_sauce_creds_set_for_testing(), "Must set 'SAUCE_USERNAME' and 'SAUCE_APIKEY' ("
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
    @staticmethod
    def get_screen_shot_paths(search_dir=os.getcwd()):
        return glob.glob("%s/*.png" % search_dir)

    def assert_screen_shots(self, expected_screen_shots):
        screen_shots = self.get_screen_shot_paths()
        if expected_screen_shots > 0:
            self.assertTrue(len(screen_shots) > 0, "A screen shot was taken")

        self.assertEquals(len(screen_shots), expected_screen_shots, "Exactly %s screen shots should have been taken, "
                                                                    "got %s instead"
                                                                    % (expected_screen_shots, screen_shots))


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
        self.assert_screen_shots(2)
        #TODO DCLT-726: Change to 1 when we fix this bug.

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


class SelectorsTestCase(BaseTestCase):

    """
    @unittest.skip("NOT IMPLEMENTED YET: See DCLT-728")
    def test_s2l_keyword_with_selector(self):
        run = self.run_scenario("test_s2l_keyword_with_selector.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")
    """

    def test_find_elements_with_selector(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_find_elements_with_selector.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_selector_exceptions(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_selector_exceptions.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_no_robot_action_failing_should_not_warn_about_screenshot(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_fail.py")
        self.assertFalse("warn" in run.output.lower(), "No warning should be issued when a method fails outside "
                                                       "robot")

    def robot_importing_se2lib_after_page_object_should_work(self):
        # This run is duplicated, but it shows that SE2Lib library imported
        # with page objects works.
        run = self.run_scenario("test_template_passed.robot")
        self.assert_run(run, expected_returncode=0, search_output="PASSED")

    def robot_importing_se2lib_before_page_object_should_work(self):
        run = self.run_scenario("test_se2lib_imported_before_po.robot")
        self.assert_run(run, expected_returncode=0, search_output="PASSED")

class ComponentTestCase(BaseTestCase):

    def test_page_components_unittest(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_components.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_page_component_unittest(self):
        # Tests get_instance, instead of get_instances.
        self.set_baseurl_env()
        run = self.run_scenario("test_component.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_page_components_robot(self):
        run = self.run_scenario("test_components.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")


""" The following classes are used by tests for the header/subheader component.
These tests are at the end of the file and are ultimately intended for the actual header/subheader
components that will be written at some point soon. For now, I am sticking them in the
Robot Framework Page Object package because it's a proof-of-concept and since the packages
aren't written yet and the version of RF PO with support for components isn't tagged yet, I
don't want to have to link to dev branches in depdendency links.
"""

class SubHeaderComponent(Component):
    """ Encapsulates the common, Sub header
    found on most NCBI pages.
    """

    # This identifies the parent
    # web element for this component.
    locator = "css=.header"

    # All selectors are implicitly limited to
    # descendents of the "root webelement" for
    # this component. This assures that you are finding
    # the element for **this** component.
    # If for some reason, you need to access the actual
    # root WebElement for this instance, access: self.root_webelement
    # from a component method.
    selectors = {
        "Search Database Select": "id=database",
        "Search Term Input": "id=term",
        "Search Button": "id=search",
    }

    # As a rule, allow easy access
    # as properties, instead of getter
    # methods.
    @property
    def selected_database(self):
        # Remember, try to use Selenium2Library methods, instead of
        # the lower level WebDriver API. You can pass selectors to
        # these as well as locators.
        return self.get_selected_list_label("Search Database Select")

    def search(self, db, term):
        self.select_from_list_by_label("Search Database Select", db)
        self.input_text("Search Term Input", term)
        self.click_button("Search Button")
        # Let the page object return the correct page object
        # after calling this method on the GlobalHeader instance.



class SubHeaderComponentManager(ComponentManager):

    # The job of the manager class is to allow the
    # page object access to the component instances.
    # Here, since there is only one GlobalHeader per page
    # we define a single property, called "subheader"
    # and return the result of get_instance(). If
    # there were multiple instances on the page, we'd
    # call get_instances().
    @property
    def subheader(self):
        return self.get_instance(SubHeaderComponent)


class HeaderComponent(Component, SubHeaderComponentManager):

    locator = ""
    selectors = {
        "logo": "css=.ncbi_logo",

    }

    def click_logo(self):
        self.click_element("logo")

    def search(self, db, term):

        # Defers to this component's sub component
        self.subheader.search(db, term)


class MySubHeaderPage(Page, SubHeaderComponentManager):

    uri = "/"

    @robot_alias("selected_database_in_subheader_should_be_on__name__")
    def selected_database_in_subheader_should_be(self, db):
        asserts.assert_equals(self.subheader.selected_database, db)

    @robot_alias("search_from_subheader_on__name__")
    def search_from_subheader(self, db, term):
        self.subheader.search(db, term)
        # Here we'd have to figure out what page object to return...

class SubHeaderComponentTestCase(unittest.TestCase):

    def setUp(self):
        #super(SubHeaderComponentTestCase, self).setUp()
        os.environ["PO_BASEURL"] = "http://www.ncbi.nlm.nih.gov"
        #os.environ["PO_BROWSER"] = "firefox"
        os.environ["PO_SELENIUM_SPEED"] = ".5"
        self.sub_header_page = MySubHeaderPage()
        self.sub_header_page.open()

    def test_selected_database(self):
        self.sub_header_page.selected_database_in_subheader_should_be("All Databases")

    def test_search_from_subheader(self):
        self.sub_header_page.search_from_subheader("Books", "dog")
        self.sub_header_page.title_should_be("dog - Books - NCBI")

    def tearDown(self):
        #super(SubHeaderComponentTestCase, self).tearDown()
        self.sub_header_page.close()









