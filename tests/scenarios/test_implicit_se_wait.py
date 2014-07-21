import unittest
from po.widget_rel_uri_attr import Page


class ImplicitWaitTestCase(unittest.TestCase):

    def setUp(self):
        import os
        os.environ["PO_BROWSER"] = "firefox"
        os.environ["PO_BASEURL"] = "file:///home/cohenaa/projects/ift/robotframework-pageobjects/tests/scenarios"
        self.p = Page()
        self.p.open()

    def test_implicit_wait_default_works(self):
        self.p.click_delayed_content_button()
        self.p.delayed_content_should_exist()

    def tearDown(self):
        self.p.close()


if __name__ == "__main__":
    unittest.main()

