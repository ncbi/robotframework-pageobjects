import inspect
from PageObjectLibrary import PageObjectLibrary
import sys


class EntrezPageLibraryMeta(type):
    """
    This is the metaclass for the EntrezPageLibrary class, from which PubmedPageLibrary, BooksPageLibrary, etc. inherit.
    It injects the method sof EntrezPageLibrary base into the class being created.
    """
    def __new__(cls, name, bases, attrs):
        if (name == "EntrezPageLibrary"):
            # Don't do any funny stuff on the base Entrez library
            return super(EntrezPageLibraryMeta, cls).__new__(cls, name, bases, attrs)
                    
        # Get all methods in the base class, and replace "_pol_" in their methods with the name declared in the class definition
        for name, func in [(meth[0], meth[1].im_func) for meth in inspect.getmembers(EntrezPageLibraryBase) if hasattr(meth[1], "im_func")]:
            attrs[name.replace("_pol_", "_" + attrs["name"] + "_")] = func
        
        return super(EntrezPageLibraryMeta, cls).__new__(cls, name, bases, attrs)


class EntrezPageLibraryBase(PageObjectLibrary):
    """
    Methods defined in this class can be used by classes that inherit from EntrezPageLibrary.
    They are injected by EntrezPageLibraryMeta into classes that extend EntrezPageLibrary.
    """
    def click_pol_docsum_item_number(self, n):
        i = int(n) + 1
        self.se.click_link("xpath=//div[@class='rprt'][%s]//p[@class='title']/a" % str(i))

    def search_pol_for(self, term):
        self.se.input_text("term", term)
        self.se.click_button("search")    

        
class EntrezPageLibrary(object):
    """
    This is the base class for PubmedPageLibrary, BooksPageLibrary, etc.
    """
    __metaclass__ = EntrezPageLibraryMeta
    
"""
def base_factory(meta, *bases):
    return meta("NewBase", bases, {})

class EntrezPageLibrary(base_factory(EntrezPageLibraryMeta)):
    def click_pol_docsum_item_number(self, n):
        i = int(n) + 1
        self.se.click_link("xpath=//div[@class='rprt'][%s]//p[@class='title']/a" % str(i))

    def search_pol_for(self, term):
        self.se.input_text("term", term)
        self.se.click_button("search")
    __metaclass__ = EntrezPageLibraryMeta
"""