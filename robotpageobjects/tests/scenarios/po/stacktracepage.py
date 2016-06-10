from robotpageobjects import Page

class StackTracePage(Page):

    uri = "site/index.html"

    def raise_division_by_zero(self):
        1/0
        return self