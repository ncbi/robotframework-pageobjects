from po.ncbi import NCBIPage
import unittest
import os


class NCBITestCase(unittest.TestCase):
    def test_title_should_fail(self):
        os.environ["PO_BASEURL"] = "http://www.ncbi.nlm.nih.gov"
        os.environ["PO_BROWSER"] = "Firefox"
        os.environ["PO_SAUCE_BROWSERVERSION"] = "27"
        os.environ["PO_SAUCE_USERNAME"] = "cohenaa2"
        os.environ["PO_SAUCE_PLATFORM"] = "Windows 8.1"
        os.environ["PO_SAUCE_APIKEY"] = "ea30c3ed-2ddb-41ca-bde1-41122dcfc1cd"
        self.p = NCBIPage()
        self.p.open({"path": "pubmed"})
        self.p.title_should_be("Home - PubMed - NCBI")

        # This should fail, so we test that we get
        # assertions failures when running remotely.
        self.p.title_should_be("foo")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()