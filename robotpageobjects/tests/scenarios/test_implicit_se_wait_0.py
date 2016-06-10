import unittest
from po.widget_rel_uri_attr import Page


class ImplicitWaitSet0TestCase(unittest.TestCase):

    def setUp(self):
        self.p = Page()

    def test_implicit_wait_is_set_to_0(self):
        self.assertEqual(self.p.get_selenium_implicit_wait(), "0 seconds")
        self.assertEqual(self.p.get_selenium_timeout(), "0 seconds")

if __name__ == "__main__":
    unittest.main()

