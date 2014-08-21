import unittest
from po import selectors_page
from robotpageobjects import base
import time

class ServiceArgsCookieFileTestCase(unittest.TestCase):

    def test_open_close_creates_cookie_file(self):
        self.p = selectors_page.Page()
        self.p.open()
        self.p.close()

if __name__ == '__main__':
    unittest.main()
