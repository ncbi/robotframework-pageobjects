from robotpageobjects import Page


class LoggingPage(Page):
    uri = ""

    def log_warning(self):
        self.log("hello world", "WARNING")
        return self

    def log_debug(self):
        self.log("hello world", "DEBUG")
        return self
