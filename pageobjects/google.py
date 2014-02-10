
from pageobjects.base.PageObjectLibrary import PageObjectLibrary, robot_alias


class Page(PageObjectLibrary):

    """
    Base Google Page

    For example, search() works on any google page.
    """
    homepage = "http://www.google.com"
    name = "Google Homepage"

    # By default, page object methods
    # map in Robot Framework to method name + class name.
    # Eg. Search Google  term. But we can use robot_alias decorator
    # with the __name__ token to map the page object name to
    # wherever you want in the method. So this would become
    # Search Google For  term.
    @robot_alias("search__name__for")
    def search(self, term):
        self.se.input_text("xpath=//input[@name='q']", term)
        self.se.click_element("gs_htif0")
        return ResultPage()

class ResultPage(Page):

    """
    A Google Result page. Inherits from Google Page.
    """
    name = "Google Result Page"

    @robot_alias("on__name__click_result")
    def click_result(self, i):
        els = self.se._element_find("xpath=//h3[@class='r']/a[not(ancestor::table)]", False, False, tag="a")
        try:
            els[int(i)].click()
        except IndexError:
            raise Exception("No result found")