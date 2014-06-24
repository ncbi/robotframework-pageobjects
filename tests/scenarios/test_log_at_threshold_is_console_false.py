import unittest
from po.loggingpage import LoggingPage


class LoggingTestCase(unittest.TestCase):

    def test_log_at_threshold(self):
        LoggingPage().log_info_is_console_false()

unittest.main()
