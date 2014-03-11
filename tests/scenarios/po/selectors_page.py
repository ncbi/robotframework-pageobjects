from robotpageobjects import Page as RobotPage

class Page(RobotPage):
    name = "Widget Page"
    uri = "/site/index.html"
    selectors = {"search-button": "css=#go"}
