import os
import unittest
import glob
from unittest import skip

from basetestcase import BaseTestCase


class BrowserOptionTestCase(BaseTestCase):
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

    def test_unittest_default_browser_should_be_phantomjs(self):
        run = self.run_scenario("test_abs_url_set.py")
        self.assert_run(run, search_output="OK", expected_browser="phantomjs")

    def test_robot_default_browser_should_be_phantomjs(self):
        run = self.run_scenario("test_no_url_passed_abs_homepage_set.robot")
        self.assert_run(run, search_output="PASS", expected_browser="phantomjs")

    def test_unittest_PO_BROWSER_env_var_set_to_firefox_should_run_in_firefox(self):
        os.environ["PO_BROWSER"] = "firefox"
        run = self.run_scenario("test_abs_url_set.py")
        self.assert_run(run, search_output="OK", expected_browser="firefox")

    def test_robot_variable_set_should_run_in_firefox(self):
        run = self.run_scenario("test_no_url_passed_abs_homepage_set.robot", variable="browser:firefox")
        self.assert_run(run, search_output="PASS", expected_browser="firefox")

    def test_unittest_variable_file_var_set_to_firefox_should_run_in_firefox(self):
        try:
            self.write_var_file(browser="firefox")
            os.environ["PO_VAR_FILE"] = self.test_dir + os.sep + "vars.py"
            run = self.run_scenario("test_abs_url_set.py")
            self.assert_run(run, search_output="OK", expected_browser="firefox")

        except AssertionError, e:
            raise e

        finally:
            self.remove_vars_file()


class ActionsTestCase(BaseTestCase):
    @skip("NOT IMPLEMENTED YET")
    def unittest_test_screenshot_on_failure(self):
        run = self.run_scenario("test_fail.py")
        self.assertEquals(len(glob.glob("*.png")), 1, "On Failure page object should take screenshot")

    @skip("NOT IMPLEMENTED YET")
    def robot_test_screenshot_on_failure(self):
        run = self.run_scenario("test_fail.robot")
        self.assertEquals(len(glob.glob("*.png")), 1, "On Failure page object should generate screenshot")


if __name__ == "__main__":
    unittest.main()









