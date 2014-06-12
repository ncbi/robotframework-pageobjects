import unittest
from po.loggingpage import LoggingPage


class LoggingTestCase(unittest.TestCase):

    def setUp(self):
        self.p = LoggingPage()

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
        self.p.log_stuff("hello world")
        self.assertEquals(self.read_from_log_file(), "hello world\n")

unittest.main()
