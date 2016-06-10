import subprocess
import unittest
from xml.dom.minidom import parse

import re
import os
import glob
import six
from nose.tools import nottest


class BaseTestCase(unittest.TestCase):


    """
    Base class Robot page object test cases.
    """

    test_dir = os.path.dirname(os.path.realpath(__file__))
    scenario_dir = os.path.join(test_dir, "scenarios")
    po_dir = os.path.join(scenario_dir, "po")

    base_file_url = "file:///%s/scenarios" % test_dir.replace("\\", "/")
    site_under_test_file_url = "%s/site/index.html" % base_file_url

    @classmethod
    @nottest
    def are_sauce_creds_set_for_testing(cls):
        """
        Determines if private sauce credentials are set as environment variables.

        It doens't check for "PO_SAUCE..." because these special env vars
        actually affect the tests. This leaves out "PO" so we can get the
        credentials and keep them around, without affecting any tests.
        """
        return "SAUCE_USERNAME" in os.environ and "SAUCE_APIKEY" in os.environ


    def get_log_path(self, is_robot=False, output_xml=False):
        if is_robot:
            if output_xml:
                filename = "output.xml"
            else:
                filename = "log.html"
        else:
            filename = "po_log.txt"

        return os.path.join(self.scenario_dir, filename)

    def read_log(self, is_robot=False, output_xml=False):
        """ Read the Robot or python log file.

         :param is_robot: Whether Robot or not.
         :type is_robot: Boolean
         :param output_xml: Whether to read Robot's output.xml instead of report.html.
         :type output_xml: Boolean
        """
        f = open(self.get_log_path(is_robot, output_xml), "r")
        try:
            ret = f.read()
        finally:
            f.close()
            return ret

    def get_sauce_creds(self):
        """
        Returns tuple of sauce username, SAUCE_APIKEY set in environment
        for testing.
        """
        return os.getenv("SAUCE_USERNAME"), os.getenv("SAUCE_APIKEY")

    def setUp(self):

        # Remove png and xml files
        screenshot_locator = os.path.join(self.scenario_dir, "selenium-screenshot*.png")
        for screenshot in glob.glob(screenshot_locator):
            os.unlink(screenshot)
        xml_locator = os.path.join(self.scenario_dir, "*.xml")
        for xml in glob.glob(xml_locator):
            os.unlink(xml)

        try:
            os.unlink(self.get_log_path())
        except OSError:
            pass
        try:
            os.unlink(self.get_log_path(is_robot=True))
        except OSError:
            pass

        # Save all env vars (including PO_ vars), so that if they are modified,
        # we can restore them in tearDown. Unset all PO_ env variables, so that
        # we don't get interference from the user's environment.

        self.original_env_vars = {}
        for key in os.environ.keys():
            self.original_env_vars[key] = os.environ[key]
            if key.lower().startswith("po_"):
                del os.environ[key]

    def tearDown(self):
        # Restore envs
        for key in self.original_env_vars:
            os.environ[key] = self.original_env_vars[key]

        for key in list(os.environ):
            if key not in self.original_env_vars:
                del os.environ[key]

        try:
            os.unlink(self.get_log_path())
        except OSError:
            pass
        try:
            os.unlink(self.get_log_path(is_robot=True))
        except OSError:
            pass

    def set_baseurl_env(self, base_file=True, arbitrary_base=None):
        val = self.base_file_url if base_file else arbitrary_base
        return self.set_env("PO_BASEURL", val)

    def set_env(self, var, val):
        os.environ[var] = val
        return os.environ.get(var)

    def run_scenario(self, scenario, *args, **kwargs):
        """
        Runs a robot page object package test scenario, either a plain Python
        unittest or a robot test. The unittest scenario must reside in tests/scenarios and have
        a .py ending. The robot test must also live under tests/scenarios and have a .robot
        ending.
        """

        env_vars = {}
        if "env" in kwargs:
            env_vars = kwargs["env"]
            del kwargs["env"]
            for var, val in six.iteritems(env_vars):
                self.set_env(var, val)

        if scenario.endswith(".py"):
            return self.run_program("python", self.scenario_dir, scenario)
        else:
            kwargs['P'] = "po"
            return self.run_program("pybot", self.scenario_dir, scenario, **kwargs)

    def run_program(self, base_cmd, working_dir, target, **opts):
        """
        Runs a program using a subprocess

        :param base_cmd: the command to run in subprocess
        :param working_dir: directory from which to run the command
        :param target: target of command
        :param opts:  keyword arguments to pass to the program
        :return: an object with the following properties:
        - cmd: The command which was run
        - returncode: The return code
        - output: the output from stdout or stderr
        """
        class Ret(object):
            """
            The object to return from running the program
            """

            def __init__(self, cmd, returncode, output):
                self.cmd = cmd
                self.returncode = returncode
                self.output = output

            def __repr__(self):
                return "<run object: cmd: '%s', returncode: %s, output: %s>" % \
                       (self.cmd, self.returncode, self.output[0:25] .replace("\n", ""))

        # prepare command
        opt_str = ""
        for name in opts:
            val = opts[name]
            if isinstance(val, bool):
                opt_str += "--" + name.replace("_", "-") + " "
            else:
                dash = "-" if len(name) == 1 else "--"
                opt_str += dash + name.replace("_", "-") + " " + val + " "
        cmd = str.join(six.u(' '), [base_cmd, opt_str, target])

        # execute command
        p = subprocess.Popen(cmd, cwd=working_dir, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        com = p.communicate()
        code = p.wait()
        # Out is either stdout, or stderr
        out = str.join(six.u(" "), [str(x) for x in com])
        # Splice out trailing new line
        out = out[:-1]
        return Ret(cmd, code, out)

    def get_screen_shot_paths(self):
        return glob.glob("%s/*.png" % self.scenario_dir)

    def assert_screen_shots(self, expected_screen_shots):
        screen_shots = self.get_screen_shot_paths()
        if expected_screen_shots > 0:
            self.assertTrue(len(screen_shots) > 0, "No screenshot was taken")

        self.assertEquals(len(screen_shots), expected_screen_shots, "Exactly %s screen shots should have been taken, "
                                                                    "got %s instead"
                                                                    % (expected_screen_shots, screen_shots))


    def assert_run(self, run,
                   expected_returncode=0, expected_tests_ran=None,
                   expected_tests_failed=None,
                   search_output=None, search_log=None, search_output_xml=None, not_in_output=None, not_in_log=None,
                   expected_browser=None
    ):
        """
        Makes general assertions about a program run based on return code
        and strings written to stdout. Always checks if run was 0
        return code.

        :param run: The object returned by runsanity()
        :param expected_returncode: expected returncode
        :param expected_tests_ran: number of tests ran
        :param expected_tests_failed: number of tests failed
        :param search_output: Text to assert is present in stdout of run. Provide  regular expression
        :param search_log: Regular expression to use to search log
        :param not_in_log: String to assert that's NOT in log. Not a regular expression.
        :param search_output_xml: Search the output XML for a string. In Robot this is output.xml.

        """
        returncode = run.returncode
        is_robot = "pybot" in run.cmd
        self.assertEquals(expected_returncode, returncode,
                          "Return code was %s, expecting %s with the command: '%s'\n"
                          "The message was:\n%s\n" % (
                              returncode, expected_returncode, run.cmd, run.output))
        if expected_tests_ran:
            self.assertTrue("Ran %s test" % expected_tests_ran in run.output, "Didn't get %s tests ran when "
                                                                              "running '%s'" % (
                                                                                  expected_tests_ran,
                                                                                  run.cmd))
        if expected_tests_failed:
            self.assertTrue("failures=%s" % expected_tests_failed in run.output,
                            "Did not find %s expected failures when running %s." % (expected_tests_failed,
                                                                                    run.cmd))
        if search_output:

            self.assertIsNotNone(re.search(search_output, run.output),
                                 "string: '%s' not found in stdout when running %s" % (
                                     search_output, run.cmd))
        if search_log:
            log_contents = self.read_log(is_robot)


            self.assertTrue(search_log in log_contents,
                                 "string: '%s' not found in log file when running %s" % (
                                     search_log, run.cmd))

        if search_output_xml:
            xml = self.read_log(is_robot, output_xml=True)
            self.assertTrue(search_output_xml in xml, "'%s' not found in output.xml" % search_output_xml)

        if not_in_log:
            self.assertFalse(not_in_log in self.read_log(is_robot), '"%s" was found in the log file, '
                                                                    'but shouldn\'t have been.'
                                                                    % not_in_log)

        if not_in_output:
            self.assertFalse(not_in_output in run.output, '%s not in output when running command: %s' %(
                not_in_output, run.cmd))

        if expected_browser:
            log_content = self.read_log(is_robot)

            if is_robot:
                self.assertTrue(expected_browser in log_content,
                                "Unexpected browser logged")

            else:

                self.assertTrue(expected_browser in log_content,
                                "Unexpected browser logged")


    def write_var_file(self, *args, **kwargs):
        f = None
        try:
            f = open(self.test_dir + os.sep + "vars.py", "w")
            for i in kwargs:
                line = "%s = '%s'\n" % (i, kwargs[i])
                f.write(line)
        except Exception as e:
            raise Exception("Problem creating vars file: %s" % e)
        finally:
            if f:
                f.close()

    def remove_vars_file(self):
        try:
            vars_path = self.test_dir + os.sep + "vars.py"
            os.unlink(vars_path)
            os.unlink(self.test_dir + os.sep + "vars.pyc")
        except OSError:
            pass


