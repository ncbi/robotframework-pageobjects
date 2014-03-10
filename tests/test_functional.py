import glob
import os
import unittest

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
        self.set_baseurl_env()
        run = self.run_scenario("test_template_passed.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_robot_uri_template(self):
        run = self.run_scenario("test_template_passed.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")


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

    @unittest.skip("NOT IMPLEMENTED YET")
    def unittest_test_screenshot_on_failure(self):
        self.assert_screen_shots(0)
        self.run_scenario("test_fail.py")
        self.assert_screen_shots(1)

    def test_robot_screen_shot_on_page_object_keyword_failure(self):
        self.assert_screen_shots(0)
        self.run_scenario("test_fail.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_screen_shots(1)

    def test_robot_screen_shot_on_se2lib_keyword_failure(self):
        self.assert_screen_shots(0)
        self.run_scenario("test_fail_se2lib_keyword.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_screen_shots(1)

class SelectorsTestCase(BaseTestCase):
    @unittest.skip("NOT IMPLEMENTED YET: See DCLT-728")
    def test_click_element_selector(self):
        run = self.run_scenario("test_click_element_selector.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

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

if __name__ == "__main__":
    unittest.main()









