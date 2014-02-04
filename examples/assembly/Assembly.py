from difflib import Differ
import sys
from Selenium2Library import Selenium2Library
from robot.utils import asserts

class Assembly(Selenium2Library):
    def get_file_contents(self, filename):
        f = open(filename, "r")
        contents = f.read()
        f.close()
        return contents
    
    def source_should_match_file(self, filename):
        """
        Diff the source of a page against the contents of a baseline file.
        Then make sure the size of the diff is the same as that of the contents.
        Why are we doing this?
        """
        contents = self.get_file_contents(filename)
        source = self.get_source()
        d = Differ()
        result = list(d.compare(source, contents))
        resultlen = len(result)
        contentslen = len(contents)
        asserts.assert_equal(resultlen, contentslen)
        
