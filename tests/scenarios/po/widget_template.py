
from robotpageobjects.page import Page


class WidgetItemPage(Page):
    name = "Widget Item Page"
    uri_template = "/site/category/{category}/{id}.html"
    selectors = {"title": "css=h1",
                 "hidden-element": "css=#hidden"}

