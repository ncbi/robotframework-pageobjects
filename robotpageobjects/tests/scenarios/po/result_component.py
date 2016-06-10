from robotpageobjects import Page, Component, robot_alias, Override
from robot.utils import asserts

class ResultComponent(Component):


    selectors = {
        "price el": "css=div.price",
    }

    @property
    def price(self):
        return self.get_text("price el")


class ResultPage(Page):
    components = {ResultComponent: "css=ul#results li.result"}

    uri = "/site/result.html"


class ResultPageWithDOMStrategyLocator(Page):
    components = {ResultComponent: "dom=window.jQuery('#results li.result:lt(2)')"}

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


class BaseSearchComponent(Component):

    selectors = {
        "search input": "id=q",
    }

    def set_search_term(self, term):
        self.input_text("search input", term)



class SearchComponent(BaseSearchComponent):
    components = {AdvancedOptionTogglerComponent: "id=advanced-options"}

    @property
    def some_property(self):
        self.log("foo", is_console=False)
        return 1


class SearchComponentWithDOMAdvancedToggler(BaseSearchComponent):
    components = {AdvancedOptionTogglerComponent: "dom=jQuery('#advanced-options')"}


class HomePage(Page):
    components = {SearchComponent: "id=search-form"}
    uri = "/site/index.html"

    def get_some_property(self):
        return self.search.some_property


class HomePageWithDOMAdvancedToggler(Page):
    components = {SearchComponentWithDOMAdvancedToggler: "id=search-form"}
    uri = "/site/index.html"


class BodyComponent(Component):
    pass


class ParaComponent(Component):
    pass


class TwoComponentsPage(Page):
    components = {BodyComponent: "css=body", ParaComponent: "css=p"}
    uri = "/site/index.html"


class TwoComponentsSubPage(TwoComponentsPage):
    components = {Override(ParaComponent): "css=p#advanced-search-content"}