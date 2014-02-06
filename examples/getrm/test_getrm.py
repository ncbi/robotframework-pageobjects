import unittest
from GeTRM import GeTRM


expected_vals = { "1q24" : "Homo sapiens: GRCh37.p\d+\s+Chr\s1\s\WNC_000001.\d+\W:\s164.7\d+M\s-\s173.6\d+M",
                 "Neurofibromatosis" : "Homo sapiens: GRCh37.p\d+\s+Chr\s17\s\WNC_000017.\d+\W:\s29.6\d+M\s-\s29.\d+M"} 

selectors = {
    "search" : "id=loc-search",
    "result-arrow" : "xpath=//table[contains(@class, 'grid-results')]/tbody/tr[1]/td[@class='ctrl']",
    "header-spans" : "css=div.track-header > span",
    "gt-spans" : "css=div.gt-right.gt-ruler > span",
    "search-arrow" : "css=img.content-search-go"
}

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.se = GeTRM()
        self.se.open_browser("http://www.ncbi.nlm.nih.gov/variation/tools/get-rm", "ff")
    def find(self, selector):
        locator = selectors[selector]
        return self.se._element_find(locator, True, True)
    
    def search(self, term):
        rm_search_box = self.find("search")
        rm_search_box.clear()
        rm_search_box.send_keys(term)
        #if os.name == "posix":
        #rm_search_box.send_keys("ENTER") # Might need to substitute here
        #else:
        self.se.click_element(selectors["search-arrow"])

    def go_to_results(self):
        self.se.wait_until_page_contains_element(selectors["result-arrow"])
        #self.se.mouse_over(selectors["result-arrow"])
        self.se.click_element(selectors["result-arrow"])

    def test_foo(self):
        for term, expected_val in expected_vals.iteritems():
            self.search(term)
            self.go_to_results()
            
    
    def tearDown(self):
        self.se.close_browser()


if __name__ == "__main__":
    unittest.main()
