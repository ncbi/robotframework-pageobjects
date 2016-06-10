from robotpageobjects import Page, Component

class FormComponent(Component):
    pass

class Page(Page):
    uri = "/site/index.html"

    components = {FormComponent: "css=form"}
