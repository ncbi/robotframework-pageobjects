from robotpageobjects import Page


class LoggingPage(Page):
    uri = ""

    def log_stuff(self, str):
        self.log("hello world")
        return self
