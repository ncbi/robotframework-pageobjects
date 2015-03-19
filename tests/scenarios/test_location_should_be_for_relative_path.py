from po.ncbi import NCBIPage
import unittest
import os
from robotpageobjects import Page

class BaseMethodLocationShouldBeTestCase(unittest.TestCase):

    baseurl = "file://%s" % os.path.join(os.path.dirname(os.path.realpath(__file__)), "site")

    def test_location_should_be_for_relative_path(self):
        os.environ["PO_BASEURL"] = self.baseurl
        Page.uri = "/index.html"
        self.p = Page()
        self.p.open()
        self.p.location_should_be("/index.html")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()
