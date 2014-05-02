from robotpageobjects import Page, PageComponent, robot_alias, not_keyword
from robot.utils import asserts

class ResultComponent(PageComponent):

    locator = "css=ul#results li.result"

    @property
    def price(self):
        return self.root_webelement.find_element_by_css_selector("div.price").text

class ResultPage(Page):

    uri = "/site/result.html"

    components = [ResultComponent]

    # This function belongs in the base Page object.
    @not_keyword
    def get_components(self, type):
        """ Returns a list of a given component
        """
        return self._components[type]

    @robot_alias("item_on__name__should_cost")
    def item_should_cost(self, i, expected_price):
        results = self.get_components("ResultComponent")
        asserts.assert_equals(results[i - 1].price, expected_price)









