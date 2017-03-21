from robotpageobjects import Page as RobotPage

class Page(RobotPage):
    name = "Widget Page"
    uri = "/site/index.html"
    selectors = {
        "search-button": "css=#go",
        "inputs": "css=input",
        "hide-button": "css=button#hide-content",
        "para-to-be-hidden": "css=p#disappear",
        "delayed-content-button":"css=button#delayed-content"
    }
