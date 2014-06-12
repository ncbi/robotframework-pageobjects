import unittest
from robotpageobjects import Page


class LoggingTestCase(unittest.TestCase):

    def setUp(self):

        class P(Page):
            uri = ""

        self.p = P()

    def read_from_log_file(self):
        log = open("po_log.txt")
        ret = None
        try:
            ret = log.read()
        except Exception, e:
            raise e
        finally:
            log.close()
            return ret

    def test_log_to_file_and_screen(self):
        self.p.log("hello", "world")
        self.assertEquals(self.read_from_log_file(), "hello\tworld\n")

unittest.main()
