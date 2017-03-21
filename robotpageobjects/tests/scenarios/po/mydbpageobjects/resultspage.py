from basepageobjects import BaseResultsPage

class MyDBResultsPage(BaseResultsPage):
    uri = "http://www.ncbi.nlm.nih.gov/mydb/?term={term}"
