from result_component import ResultPage
class ResultPageWithSingularPropertyDefined(ResultPage):
    @property
    def result(self):
        return None
