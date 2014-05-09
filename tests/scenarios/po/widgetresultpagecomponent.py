from robotpageobjects import Page, Component, robot_alias, ComponentManager
from robot.utils import asserts

class ResultComponent(Component):


    selectors = {
        "price el": "css=div.price",
    }

    @property
    def price(self):
        return self.get_text("price el")

class ResultsComponentManager(ComponentManager):

    locator = "css=ul#results li.result"

    @property
    def results(self):
       return self.get_instances(ResultComponent)

class ResultComponentManager(ComponentManager):

    locator = "css=ul#results li.result"

    @property
    def result(self):
        return self.get_instance(ResultComponent)


class ResultsPage(Page, ResultsComponentManager):

    uri = "/site/result.html"

    @robot_alias("item_on__name__should_cost")
    def item_should_cost(self, i, expected_price):
        results = self.results

        # OK, here we really should check for a KeyError, but
        # we know it won't produce one here in the mocked
        # test case...so we won't.
        asserts.assert_equals(results[int(i) - 1].price, expected_price)

class ResultPage(Page, ResultComponentManager):

    uri = "/site/result.html"

    @robot_alias("item_on__name__should_cost")
    def item_should_cost(self, i, expected_price):
        results = self.results

        # OK, here we really should check for a KeyError, but
        # we know it won't produce one here in the mocked
        # test case...so we won't.
        asserts.assert_equals(results[int(i) - 1].price, expected_price)




