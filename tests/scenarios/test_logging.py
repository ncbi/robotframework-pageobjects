import unittest
from robotpageobjects import Page


class LoggingTestCase(unittest.TestCase):

    def setUp(self):

        class P(Page):
            uri = ""

            def foo(self):
                self.log("hello world")
                return self

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
        self.p.foo()
        self.assertEquals(self.read_from_log_file(), "hello world\n")

unittest.main()
