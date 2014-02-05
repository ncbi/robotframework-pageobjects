import unittest
from nose2.tools import params
from difflib import Differ
from robot.utils import asserts


from Assembly import Assembly
assembly_acc = ["GCF_000001405.24", "GCF_000001405.8"]

selectors = {
    'assembly-dwnload-data' : "xpath=//div[@id = 'ui-portlet_content-1']/ul/li/a"
}

class TestAssemblyDataDownLoad(unittest.TestCase):
    
    def setUp(self):
        self.se = Assembly()
        self.base_url = "http://www.ncbi.nlm.nih.gov"
    
    @params("GCF_000001405.24", "GCF_000001405.8")
    def test_report_download(self, assembly_acc):
        url = self.base_url + "/assembly/" + assembly_acc
        self.se.open_browser(url)
        self.se.wait_until_page_contains_element(selectors["assembly-dwnload-data"])
        self.se.click_element(selectors["assembly-dwnload-data"])
        self.se.source_should_match_file(assembly_acc + ".assembly.txt")
        self.se.close_browser()