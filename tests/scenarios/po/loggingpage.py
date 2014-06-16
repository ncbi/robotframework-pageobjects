from robotpageobjects import Page


class LoggingPage(Page):
    uri = ""

    def log_stuff_to_stdout_and_file(self, str):
        self.log("hello world")
        return self

    def log_stuff_only_to_file(self, str):
        self.log("hello world", is_console=False)
        return self

    def log_debug(self):
        self.log("hello world", "INFO")
        return self
