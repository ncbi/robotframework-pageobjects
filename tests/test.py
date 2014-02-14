from basetestcase import BaseTestCase
import os
log_path = os.path.dirname(os.path.realpath(__file__)) + "/po_log.txt"


class TestBrowser(BaseTestCase):
    """
    Base class setUp removes all PO environment variables.
    tearDown restores them. It also removes po_log file in
    setUp and tearDown.
    """

    def test_unittest_default_should_run_in_phantomjs(self):
        run = self.run_program("python test_unittest.py")
        self.assert_run(run, expected_run_status="OK", expected_browser="phantomjs")

    def test_unittest_single_env_var_run_in_firefox(self):
        os.environ["PO_BROWSER"] = "firefox"
        run = self.run_program("python test_unittest.py")
        self.assert_run(run, expected_run_status="OK", expected_browser="firefox")

    def test_robot_default_should_run_in_phantomjs(self):
        run = self.run_program("pybot test_robot.robot")
        self.assert_run(run, expected_run_status="OK", expected_browser="phantomjs")










