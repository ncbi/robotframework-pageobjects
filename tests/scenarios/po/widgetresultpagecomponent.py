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

    @robot_alias("item_on__name__should_cost")
    def item_should_cost(self, i, expected_price):
        results = self.get_components("ResultComponent")

        # OK, here we really should check for a KeyError, but
        # we know it won't produce one here in the mocked
        # test case...so we won't.
        asserts.assert_equals(results[int(i) - 1].price, expected_price)









