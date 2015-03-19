import unittest
import os

from robotpageobjects import Page

class BaseMethodLocationShouldBeTestCase2(unittest.TestCase):
    baseurl = "file://%s" % os.path.join(os.path.dirname(os.path.realpath(__file__)), "site")

    def test_location_should_be_for_absolute_path(self):
        os.environ["PO_BASEURL"] = self.baseurl
        Page.uri = "/index.html"
        self.p = Page()
        self.p.open()
        self.p.location_should_be(os.path.join(self.baseurl, "index.html"))

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()
