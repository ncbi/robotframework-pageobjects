from robotpageobjects import Page, robot_alias

class MyBasePage(Page):
    uri = "/index.html"
    def footer_text_should_be(self, text):
        pass

class SubA(MyBasePage):
    def search_for(self, term):
        self.input_text("q", "search term")
        self.click_element("go")
        return SubB


class SubB(MyBasePage):
    pass