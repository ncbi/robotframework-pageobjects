from robotpageobjects import Page as RobotPage

class Page(RobotPage):
    name = "Widget Page"
    uri = "/site/index.html"
    _selectors = {"search-button": "css=#go"}
