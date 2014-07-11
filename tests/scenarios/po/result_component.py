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

    # Normally you would define "results" property,
    # but here we define a "result" property too, just
    # to test that get_instance() returns only
    # one object. You would use
    # get_instance() to return only one instance
    # if you know you have only one component instance
    # on the page.

    @property
    def result(self):
        return self.get_instance(ResultComponent, "css=ul#results li.result")

    @property
    def results(self):
        return self.get_instances(ResultComponent, "css=ul#results li.result")


class ResultComponentManagerWithDOMStrategyLocator(ResultComponentManager):
    @property
    def result(self):
        return self.get_instance(ResultComponent, "dom=window.jQuery('#results li.result:lt(2)')")
    
    @property
    def results(self):
        return self.get_instances(ResultComponent, "dom=window.jQuery('#results li.result:lt(2)')")



class ResultPage(Page, ResultComponentManager):

    uri = "/site/result.html"

class ResultPageWithDOMStrategyLocator(Page, ResultComponentManagerWithDOMStrategyLocator):
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

    @property
    def advanced_option_toggler_component(self):
        return self.get_instance(AdvancedOptionTogglerComponent, "id=advanced-options")

class BaseSearchComponent(Component):

    selectors = {
        "search input": "id=q",
    }

    def set_search_term(self, term):
        self.input_text("search input", term)



class SearchComponent(BaseSearchComponent, AdvancedOptionTogglerComponentManager):
    @property
    def some_property(self):
        self.log("foo", is_console=False)
        return 1


class SearchComponentManager(ComponentManager):

    @property
    def search_component(self):
        return self.get_instance(SearchComponent, "id=search-form")


class AdvancedOptionTogglerComponentManagerWithDOMStrategy(AdvancedOptionTogglerComponentManager):

    locator = "dom=jQuery('#advanced-options')"


class SearchComponentWithDOMAdvancedToggler(BaseSearchComponent, AdvancedOptionTogglerComponentManagerWithDOMStrategy):
    pass

class SearchComponentWithDOMAdvancedTogglerManager(ComponentManager):

    @property
    def search_component(self):
        return self.get_instance(SearchComponentWithDOMAdvancedToggler, "id=search-form")



class HomePage(Page, SearchComponentManager):
    uri = "/site/index.html"

    def get_some_property(self):
        return self.search_component.some_property

class HomePageWithDOMAdvancedToggler(Page, SearchComponentWithDOMAdvancedTogglerManager):
    uri = "/site/index.html"


class BodyComponent(Component):
    pass


class ParaComponent(Component):
    pass


class BodyComponentManager(ComponentManager):
    locator = "css=body"

    @property
    def body(self):
        return self.get_instance(BodyComponent)


class ParaComponentManager(ComponentManager):

    @property
    def paras(self):
        return self.get_instances(ParaComponent, "css=p")


class TwoComponentManagersPage(Page, BodyComponentManager, ParaComponentManager):
    uri = "/site/index.html"

