from robotpageobjects import Page


class LoggingPage(Page):
    uri = ""

    def log_warning(self):
        self.log("hello world", "WARNING")
        return self

    def log_debug(self):
        self.log("hello world", "DEBUG")
        return self

    def log_info_is_console_false(self):
        self.log("hello world", is_console=False)
        return self

    def log_debug_is_console_false(self):
        self.log("hello world", "DEBUG", is_console=False)
        return self

    def log_info(self):
        self.log("hello world")
        return self

    def log_invalid(self):
        self.log("hello workd", "BAR")
        return self
