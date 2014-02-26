
import sys
print "HEEEYA******"
for path in sys.path:
    print path

from pageobjects.PageObjectLibrary import PageObjectLibrary


class WidgetItemPage(PageObjectLibrary):
    name = "Widget Item Page"
    uri_template = "/site/category/{category}/{id}.html"


