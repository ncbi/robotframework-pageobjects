import unittest
from po.loggingpage import LoggingPage
import os


class LoggingTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_LOG_LEVEL"] = "CRITICAL"
        self.p = LoggingPage()

    def test_log_to_file_and_screen(self):
        self.p.log_stuff_to_stdout_and_file("hello world")

unittest.main()
