import re
from Selenium2Library import Selenium2Library
from Selenium2Library.locators.tableelementfinder import TableElementFinder
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

def do_monkeypatches():
    """
    DCLT-659 and DCLT-726, DCLT-827 (Solve Issue of Screenshot...):
    Add get_keyword_names and run_keyword to Se2Lib, so that we
    can use run_keyword to capture a page screenshot on failure,
    instead of a decorator and metaclass (which were causing
    duplicate screenshots).
    """
    __old_init = Selenium2Library.__init__.__func__
    def __new_init(self, *args, **kwargs):
        kwargs["run_on_failure"] = "Nothing"
        return __old_init(self, *args, **kwargs)

    Selenium2Library.__init__ = __new_init

    def __get_keyword_names(self):
        import inspect
        ret = []
        methods = inspect.getmembers(self, inspect.ismethod)
        for name, meth in methods:
            if not name.startswith("_"):
                ret.append(name)
        return ret

    Selenium2Library.get_keyword_names = __get_keyword_names

    def __run_keyword(self, alias, args):
        meth = getattr(self, re.sub(r"\s+", "_", alias))
        try:
            return meth(*args)
        except Exception, err:
            self.capture_page_screenshot()
            raise

    Selenium2Library.run_keyword = __run_keyword

    def __make_phantomjs(self , remote , desired_capabilities , profile_dir):
        browser = None
        tries = 0
        while not browser and tries < 6:
            try:
                browser = self._generic_make_browser(webdriver.PhantomJS,
                        webdriver.DesiredCapabilities.PHANTOMJS, remote, desired_capabilities)
            except WebDriverException, e:
                print "Couldn't connect to webdriver. WebDriverException was: " + str(e)
                browser = None
                tries += 1
        if browser:
            return browser
        else:
            raise WebDriverException("Couldn't connect to webdriver after several attempts")

    Selenium2Library._make_phantomjs = __make_phantomjs

    __old_tef_init = TableElementFinder.__init__.__func__
    def __new_tef_init(self, *args, **kwargs):
        __old_tef_init(self, *args, **kwargs)
        self._locator_suffixes[('css', 'last-row')] = [' tr:nth-last-child(%s)']
    
    TableElementFinder.__init__ = __new_tef_init
    
    def __find_by_row(self, browser, table_locator, row, content):
        
        location_method = "row"
        if "-" == row[0]:
            row = row[1:]
            location_method = "last-row"
        locators = self._parse_table_locator(table_locator, location_method)
        locators = [locator % str(row) for locator in locators]
        return self._search_in_locators(browser, locators, content)
    
    TableElementFinder.find_by_row = __find_by_row