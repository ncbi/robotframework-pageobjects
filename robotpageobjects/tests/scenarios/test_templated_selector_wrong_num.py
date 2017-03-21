import unittest
from po.widget_rel_uri_attr import Page
from nose.tools import raises
from robotpageobjects import exceptions

class TemplatedSelectorTestCaseWrongVars(unittest.TestCase):

    def setUp(self):
        self.p = Page()
        self.p.open()

    @raises(exceptions.SelectorError)
    def test_templated_selector_test_case(self):
        self.assertEquals(self.p.get_templated_selector_element_text_wrong_num_vars(), "I am another paragraph")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()