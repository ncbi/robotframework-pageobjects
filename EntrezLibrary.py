from Selenium2Library import Selenium2Library

import sys

class EntrezLibrary(Selenium2Library):

    def to_stdout(self, arg):
        sys.__stdout__.write(arg)

    def foo(self):
        print "foo"