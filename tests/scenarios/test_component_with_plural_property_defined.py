from result_component import ResultPage
class ResultPageWithPluralPropertyDefined(ResultPage):
    @property
    def results(self):
        return []