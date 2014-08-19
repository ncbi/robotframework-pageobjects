from robotpageobjects import Page as RobotPage

class Page(RobotPage):
    name = "Widget Page"
    uri = "/site/index.html"
    selectors = {
        "search-button": "css=#go",
        "inputs": "css=input",
        "remove-button": "css=button#remove-content",
        "para-to-be-removed": "css=p#disappear",
        "delayed-content-button":"css=button#delayed-content"
    }
