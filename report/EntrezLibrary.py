from Selenium2Library import Selenium2Library
from robot.utils import asserts
from robot.libraries.BuiltIn import BuiltIn
import sys

class EntrezLibrary(Selenium2Library):

    def to_stdout(self, arg):
        sys.__stdout__.write(arg)

    def open_pubmed_with(self, browser="phantomjs"):
        self.open_browser("http://www.ncbi.nlm.nih.gov/pubmed", browser)
        self.set_selenium_speed(1)
        self.maximize_browser_window()
        self.title_should_be("Home - PubMed - NCBI")

    def search_for(self, term):
        self.input_text("term", term)
        self.click_button("search")

    def click_see_more_search_details(self):
        self.wait_until_page_contains_element("xpath=id('search_details')/a[@class='seemore']")
        self.click_link("xpath=id('search_details')/a[@class='seemore']")

    def search_details_should_be(self, expected):
        txt = self.get_text("DetailsTerm")
        asserts.fail_unless_equal(txt, expected, msg=None, values=True)

