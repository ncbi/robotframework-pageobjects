from po.ncbi import NCBIPage
import unittest
import os


class BaseMethodLocationShouldBeTestCase(unittest.TestCase):
    def test_location_should_be_for_relative_path(self):
        os.environ["PO_BASEURL"] = "http://www.ncbi.nlm.nih.gov"
        self.p = NCBIPage()
        self.p.open({"path": "pubmed"})
        self.p.location_should_be("/pubmed")

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()