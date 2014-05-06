from robotpageobjects import Page, Component, robot_alias, ComponentManager
from robot.utils import asserts

class ResultComponent(Component):

    locator = "css=ul#results li.result"

    @property
    def price(self):
        return self.root_webelement.find_element_by_css_selector("div.price").text

class ResultComponentManager(ComponentManager):

    @property
    def results(self):
       return self._get_instances(ResultComponent)


class ResultPage(Page, ResultComponentManager):

    uri = "/site/result.html"

    @robot_alias("item_on__name__should_cost")
    def item_should_cost(self, i, expected_price):
        results = self.results

        # OK, here we really should check for a KeyError, but
        # we know it won't produce one here in the mocked
        # test case...so we won't.
        asserts.assert_equals(results[int(i) - 1].price, expected_price)










