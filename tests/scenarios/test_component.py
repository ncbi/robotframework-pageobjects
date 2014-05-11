import unittest
from po.result_component import ResultPage


class TestWidgetSearch(unittest.TestCase):

    def setUp(self):
        super(TestWidgetSearch, self).setUp()
        self.p = ResultPage()
        self.p.open()

    def test_page_component(self):
        # Tests get_instance(), as opposed to get_instances()

        self.assertNotEquals(type(self.p.result), list)
        self.assertEquals(self.p.result.price, "$14.00")

    def tearDown(self):
        super(TestWidgetSearch, self).tearDown()
        self.p.close()

if __name__ == "__main__":
    unittest.main()
