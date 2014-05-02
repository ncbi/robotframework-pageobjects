import glob
import json
import os
import re
import unittest

import requests

from basetestcase import BaseTestCase


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
                ses = re.search(r"session ID: (.{32})", content).group(1)
                return ses
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
        print run
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

class PageComponentTestCase(BaseTestCase):

    def test_page_component_unittest(self):
        self.set_baseurl_env()
        run = self.run_scenario("test_result_component.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_page_component_robot(self):
        run = self.run_scenario("test_result_component.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

if __name__ == "__main__":
    unittest.main()









