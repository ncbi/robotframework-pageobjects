import unittest
from po.widgetresultpagecomponent import ResultPage


class TestWidgetSearch(unittest.TestCase):

    def setUp(self):
        super(TestWidgetSearch, self).setUp()
        import os
        os.environ["PO_BASEURL"] = "file:////home/cohenaa/projects/ift/robotframework-pageobjects/tests/scenarios"
        self.p = ResultPage()
        self.p.open()

    def test_page_component(self):
        self.p.item_should_cost(2, "$17.00")

    def tearDown(self):
        super(TestWidgetSearch, self).tearDown()
        self.p.close()

if __name__ == "__main__":
    unittest.main()
