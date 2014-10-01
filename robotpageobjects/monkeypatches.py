import re
import pdb
import sys
from Selenium2Library import Selenium2Library
from Selenium2Library.locators.tableelementfinder import TableElementFinder
from Selenium2Library.keywords._tableelement import _TableElementKeywords
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

    def get_keyword_names(self):
        import inspect
        ret = []
        methods = inspect.getmembers(self, inspect.ismethod)
        for name, meth in methods:
            if not name.startswith("_"):
                ret.append(name)
        return ret

    Selenium2Library.get_keyword_names = get_keyword_names

    def run_keyword(self, alias, args):
        meth = getattr(self, re.sub(r"\s+", "_", alias))
        try:
            return meth(*args)
        except Exception, err:
            self.capture_page_screenshot()
            raise

    Selenium2Library.run_keyword = run_keyword

    def _make_phantomjs(self , remote , desired_capabilities , profile_dir):
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

    Selenium2Library._make_phantomjs = _make_phantomjs

    ### BEGIN QAR-48165 monkey patch
    ### This adds consistent support for negative indexes in Robot keywords. 
    
    __old_tef_init = TableElementFinder.__init__.__func__
    def __new_tef_init(self, *args, **kwargs):
        """
        The _locator_suffixes data attribute is used at the end of built-in 
        locator strings used by Selenium2Library.
        
        Monkey patch: added support for negative indexes (QAR-48165). The 
        additional locator suffixes are used by the monkey-patched methods
        'find_by_row' and 'find_by_col' defined below.  
        """
        __old_tef_init(self, *args, **kwargs)
        self._locator_suffixes[('css', 'last-row')] = [' tr:nth-last-child(%s)']
        self._locator_suffixes[('xpath', 'last-row')] = [' //tbody/tr[position()=last()-(%s-1)]']
        self._locator_suffixes[('xpath', 'row')] = [' //tbody/tr[%s]']
        self._locator_suffixes[('css', 'last-col')] = [' tr td:nth-last-child(%s)', ' tr th:nth-last-child(%s)']
        self._locator_suffixes[('xpath', 'last-col')] = [' //tbody/tr/td[position()=last()-(%s-1)]', ' //tbody/tr/td[position()=last()-(%s-1)]']

    TableElementFinder.__init__ = __new_tef_init

    def find_by_row(self, browser, table_locator, row, content):
        """ 
        Selenium2Library locator method used by _TableElementKeywords.table_row_should_contain
        This in turn is used by the built-in Robot keyword 'Table Row Should Contain'.
        
        Monkey patch: added support for negative indexes (QAR-48165).
        """  
        location_method = "row"
        if "-" == row[0]:
            row = row[1:]
            location_method = "last-row"
        locators = self._parse_table_locator(table_locator, location_method)
        locators = [locator % str(row) for locator in locators]
        return self._search_in_locators(browser, locators, content)

    TableElementFinder.find_by_row = find_by_row

    def find_by_col(self, browser, table_locator, col, content):
        """ 
        Selenium2Library locator method used by _TableElementKeywords.table_row_should_contain
        
        Monkey patch: added support for negative indexes (QAR-48165).
        """  
        location_method = "col"
        if "-" == col[0]:
            col = col[1:]
            location_method = "last-col"
        locators = self._parse_table_locator(table_locator, location_method)
        locators = [locator % str(col) for locator in locators]
        return self._search_in_locators(browser, locators, content)
    
    TableElementFinder.find_by_col = find_by_col

    def get_table_cell(self, table_locator, row, column, loglevel='INFO'):
        """Returns the content from a table cell.

        Row and column number start from 1. Header and footer rows are
        included in the count. A negative row or column number can be used
        to get rows counting from the end (end: -1) This means that also 
        cell content from header or footer rows can be obtained with this 
        keyword. To understand how tables are identified, please take a look at
        the `introduction`.
        
        Monkey patch: added support for negative indexes (QAR-48165).  
        get_table_cell is used by the built-in keyword 'Table Cell Should Contain'.
        """
        row = int(row)
        row_index = row
        if row > 0: row_index = row - 1
        column = int(column)
        column_index = column
        if column > 0: column_index = column - 1
        table = self._table_element_finder.find(self._current_browser(), table_locator)
        if table is not None:
            rows = table.find_elements_by_xpath("./thead/tr")
            if row_index >= len(rows) or row_index < 0: 
                rows.extend(table.find_elements_by_xpath("./tbody/tr"))
            if row_index >= len(rows) or row_index < 0: 
                rows.extend(table.find_elements_by_xpath("./tfoot/tr"))
            if row_index < len(rows):
                columns = rows[row_index].find_elements_by_tag_name('th')
                if column_index >= len(columns) or column_index < 0: 
                    columns.extend(rows[row_index].find_elements_by_tag_name('td'))
                if column_index < len(columns):
                    return columns[column_index].text
        self.log_source(loglevel)
        raise AssertionError("Cell in table %s in row #%s and column #%s could not be found."
            % (table_locator, str(row), str(column)))

    _TableElementKeywords.get_table_cell = get_table_cell
    ### END QAR-48165 monkey patch

    old_set_trace = pdb.set_trace
    def _set_trace():
        for attr in ('stdin', 'stdout', 'stderr'):
            setattr(sys, attr, getattr(sys, '__%s__' % attr))
        old_set_trace()
    pdb.set_trace = _set_trace