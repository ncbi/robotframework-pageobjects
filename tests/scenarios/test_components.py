import unittest
from po.result_component import ResultsPage


class TestWidgetSearch(unittest.TestCase):

    def setUp(self):
        super(TestWidgetSearch, self).setUp()
        self.p = ResultsPage()
        self.p.open()

    def test_page_component(self):
        self.p.item_should_cost(2, "$17.00")

    def tearDown(self):
        super(TestWidgetSearch, self).tearDown()
        self.p.close()

if __name__ == "__main__":
    unittest.main()
