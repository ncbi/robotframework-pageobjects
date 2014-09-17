from po.ncbi import NCBIPage
import unittest
import os


class BaseMethodLocationShouldBeTestCase2(unittest.TestCase):

    def test_location_should_be_for_obsolute_path(self):
        os.environ["PO_BASEURL"] = "http://www.ncbi.nlm.nih.gov"
        self.p = NCBIPage()
        self.p.open({"path": "pubmed"})
        self.p.location_should_be("http://www.ncbi.nlm.nih.gov/pubmed")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()