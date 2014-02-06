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


        
class EntrezPageLibrary(PageObjectLibrary):
    """
    This is the base class for PubmedPageLibrary, BooksPageLibrary, etc.
    """

    def click__po__docsum_item(self, n):
        i = int(n) + 1
        self.se.click_link("xpath=//div[@class='rprt'][%s]//p[@class='title']/a" % str(i))
        return self

    def search(self, term):
        self.se.input_text("term", term)
        self.se.click_button("search")
        return self

