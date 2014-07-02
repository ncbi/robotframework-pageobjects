import unittest
from po.widget_rel_uri_attr import Page


class TemplatedSelectorTestCase(unittest.TestCase):

    def setUp(self):
        import os
        os.environ["PO_BASEURL"] = "file:////home/cohenaa/projects/ift/robotframework-pageobjects/tests/scenarios"
        self.p = Page()
        self.p.open()

    def test_templated_selector_test_case(self):
        self.assertEquals(self.p.get_templated_selector_element_text(), "I am another paragraph")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()