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


class ResultComponentManagerWithLocatorAsCallback(ResultComponentManager):

    def locator(self):
        # Get the same results we'd get in the other cases, but use JQuery to do it
        # and to make sure we are using this overriden method, limit the results to 2, so
        # we can check the length in the test.
        return self.execute_javascript("return window.jQuery('#results li.result:lt(2)');")


class ResultPage(Page, ResultComponentManager):

    uri = "/site/result.html"

class ResultPageWithLocatorAsCallback(Page, ResultComponentManagerWithLocatorAsCallback):
    uri = "/site/result.html"



class AdvancedOptionTogglerComponent(Component):

    selectors = {
        # In relation to reference webelement, which is sibling.
        "advanced options": "xpath=./following-sibling::p[1]",
    }

    def open(self):
        self.reference_webelement.click()

    @property
    def advanced_text(self):
        return self.get_text("advanced options")


class AdvancedOptionTogglerComponentManager(ComponentManager):
    locator = "id=advanced-options"

    @property
    def advanced_option_toggler_component(self):
        return self.get_instance(AdvancedOptionTogglerComponent)


class SearchComponent(Component, AdvancedOptionTogglerComponentManager):

    selectors = {
        "search input": "id=q",
    }

    def set_search_term(self, term):
        self.input_text("search input", term)

class SearchComponentManager(ComponentManager):

    locator = "id=search-form"

    @property
    def search_component(self):
        return self.get_instance(SearchComponent)


class HomePage(Page, SearchComponentManager):
    uri = "/site/index.html"




