import unittest
from robotpageobjects.tests.scenarios.po.widget_rel_uri_attr import Page


class SelectorSelfRefTestCase(unittest.TestCase):

    def setUp(self):
        self.p = Page()
        self.p.open()

    def test_selector_self_ref(self):
        print(self.p.selectors['form label'])
        self.p.element_should_be_visible("form label")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()
