from robotpageobjects import Page, robot_alias
from robot.utils import asserts


class PubmedHomePage(Page):
    """ Models the Pubmed home page at:
        HOST://ncbi.nlm.nih.gov/pubmed"""


    # Allows us to call this page
    # something other than the default "Pubmed Home Page"
    # at the end of keywords.
    name = "Pubmed"

    # This page is found at baseurl + "/pubmed"
    uri = "/pubmed"

    # inheritable dictionary mapping human-readable names
    # to Selenium2Library locators. You can then pass in the
    # keys to Selenium2Library actions instead of the locator
    # strings.
    selectors = {
        "search input": "id=term",
        "search button": "id=search",
    }


    # Use robot_alias and the "__name__" token to customize
    # where to insert the optional page object name
    # when calling this keyword. Without the "__name__"
    # token this method would map to either "Type In Search Box",
    # or "Type In Search Box Pubmed". Using "__name__" we can call
    # "Type in Pubmed Search Box  foo".
    @robot_alias("type_in__name__search_box")
    def type_in_search_box(self, txt):
        self.input_text("search input", txt)

        # We always return something from a page object, 
        # even if it's the same page object instance we are
        # currently on.
        return self

    @robot_alias("click__name__search_button")
    def click_search_button(self):
        self.click_button("search button")

        # When navigating to another type of page, return
        # the appropriate page object.
        return PubmedDocsumPage()

    @robot_alias("search__name__for")
    def search_for(self, term):
        self.type_in_search_box(term)
        return self.click_search_button()


class PubmedDocsumPage(Page):
    """Models a Pubmed search result page. For example:
    http://www.ncbi.nlm.nih.gov/pubmed?term=cat """

    uri = "/pubmed/?term={term}"

    # This is a "selector template". We are parameterizing the 
    # nth result in this xpath. We call this from click_result, below.
    selectors = {
        "nth result link": "xpath=(//div[@class='rslt'])[{n}]/p/a",
    }

    @robot_alias("click_result_on__name__")
    def click_result(self, i):

        # For selector templates, we need to resolve the selector to the
        # locator first, before finding or acting on the element.
        locator = self.resolve_selector("nth result link", n=int(i))
        self.click_link(locator)
        return PubmedArticlePage()

class PubmedArticlePage(Page):

    uri = "/pubmed/{article_id}"

    @robot_alias("__name__body_should_contain")
    def body_should_contain(self, str, ignore_case=True):
        ref_str = str.lower() if ignore_case else str
        ref_str = ref_str.encode("utf-8")
        body_txt = self.get_text("css=body").encode("utf-8").lower()
        asserts.assert_true(ref_str in body_txt, "body text does not contain %s" %ref_str)
        return self
