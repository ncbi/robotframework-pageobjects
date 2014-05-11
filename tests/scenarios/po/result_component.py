from robotpageobjects import Page, Component, robot_alias, ComponentManager
from robot.utils import asserts

class ResultComponent(Component):


    selectors = {
        "price el": "css=div.price",
    }

    @property
    def price(self):
        return self.get_text("price el")


class ResultComponentManager(ComponentManager):

    locator = "css=ul#results li.result"

    # Normally you would define "results" property,
    # but here we define a "result" property too, just
    # to test that get_instance() returns only
    # one object. You would use
    # get_instance() to return only one instance
    # if you know you have only one component instance
    # on the page.

    @property
    def result(self):
        return self.get_instance(ResultComponent)

    @property
    def results(self):
        return self.get_instances(ResultComponent)


class ResultComponentManagerWithOverriddenGetRefEls(ResultComponentManager):

    def get_reference_webelements(self, component_class):
        return self.execute_javascript("return window.jQuery('#results li.result');")


class ResultPage(Page, ResultComponentManager):

    uri = "/site/result.html"

class ResultPageWithOverriddenGetRefEls(Page, ResultComponentManagerWithOverriddenGetRefEls):
    uri = "/site/result.html"




