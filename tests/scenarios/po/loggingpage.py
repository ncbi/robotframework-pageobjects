from robotpageobjects import Page


class LoggingPage(Page):
    uri = ""

    def log_stuff_to_stdout_and_file(self, str):
        self.log("hello world")
        return self

    def log_stuff_only_to_file(self, str):
        self.log("hello world", console=False)
