import unittest
from nose2.tools import params
from difflib import Differ


from Selenium2Library import Selenium2Library
assembly_acc = ["GCF_000001405.24", "GCF_000001405.8"]

selectors = {
    'assembly-dwnload-data' : "xpath=//div[@id = 'ui-portlet_content-1']/ul/li"
}

class TestAssemblyDataDownLoad(unittest.TestCase):
    
    def setUp(self):
        self.se = Selenium2Library()
        self.base_url = "http://www.ncbi.nlm.nih.gov"
    
    @params("GCF_000001405.24", "GCF_000001405.8")
    def test_report_download(self, assembly_acc):
        url = self.base_url + "/assembly/" + assembly_acc
        self.se.open_browser(url)
        self.se.wait_until_page_contains_element(selectors["assembly-dwnload-data"])
        self.se.click_element(selectors["assembly-dwnload-data"])
        self.full_report_download(assembly_acc)
        
    def full_report_download(self, assembly_acc):
        self.se.click_element(selectors["assembly-dwnload-data"])
        report_txt = self.se.get_source()
        report_txt = report_txt.encode("utf-8")
        baseline_name = assembly_acc + ".assembly.txt"
        f = open(baseline_name, 'r')
        baseline_txt = f.read()
        d = Differ()
        result = list(d.compare(report_txt, baseline_txt))
        resultlen = len(result)
        baselen = len(baseline_txt)
        assertEquals(resultlen, baselen)
        
    