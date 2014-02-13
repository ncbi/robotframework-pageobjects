
from pageobjects.base.PageObjectLibrary import PageObjectLibrary, robot_alias
from selenium.webdriver.common.keys import Keys


class Page(PageObjectLibrary):

    """
    Base Google Page

    For example, search() works on any google page.
    """
    homepage = "http://www.google.com"

    # name attribute tells Robot Keywords what name to put
    # after the defined method. So, def foo.. aliases to "Foo Google".
    # If no name is defined, the name will be the name of the page object
    # class.
    name = "Google"

    # By default, page object methods
    # map in Robot Framework to method name + class name.
    # Eg. Search Google  term. But we can use robot_alias decorator
    # with the __name__ token to map the page object name to
    # wherever you want in the method. So this would become
    # Search Google For  term.
    @robot_alias("search__name__for")
    def search(self, term):
<<<<<<< HEAD
        
        self.se.input_text("xpath=//input[@name='q']", term)
        self.se.click_element("xpath=//input[@name='btnG']")
=======
        self.input_text("xpath=//input[@name='q']", term)
        self.click_element("gs_htif0")
>>>>>>> ecb0450cf190176cbe1a936e5c953ac1bbf07370
        return ResultPage()

class ResultPage(Page):

    """
    A Google Result page. Inherits from Google Page.
    """
    name = "Google Result Page"

    # This will become "On Google Result Page Click Result"
    @robot_alias("on__name__click_result")
    def click_result(self, i):
<<<<<<< HEAD
        els = self.se._element_find("xpath=//ol/li/h3[@class='r']/a", False, False, tag="a")
=======
        els = self.find_elements("xpath=//h3[@class='r']/a[not(ancestor::table)]", required=False, tag="a")
>>>>>>> ecb0450cf190176cbe1a936e5c953ac1bbf07370
        try:
            els[int(i)].click()
        except IndexError:
            raise Exception("No result found")