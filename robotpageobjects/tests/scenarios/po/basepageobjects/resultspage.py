from robotpageobjects import Page

class BaseResultsPage(Page):
    """Search result page"""
    uri = "http://www.ncbi.nlm.nih.gov/{db}/?term={term}"

