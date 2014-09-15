from po.ncbi import NCBIPage
import unittest
import os


class BaseMethodLocationShouldBeTestCase2(unittest.TestCase):

    def test_location_should_be_for_obsolete_path(self):
        os.environ["PO_BASEURL"] = "http://www.ncbi.nlm.nih.gov"
        os.environ["PO_BROWSER"] = "Firefox"
        self.p = NCBIPage()
        self.p.open({"path": "pubmed"})
        self.p.location_should_be("http://www.ncbi.nlm.nih.gov/pubmed")

        # This should fail, so we test that we get
        # assertions failures when running remotely.
        self.p.location_should_be("http://www.ncbi.nlm.nih.gov/pub")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()