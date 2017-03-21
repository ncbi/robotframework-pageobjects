*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    widget_template.WidgetItemPage
# Keep SE2Lib imported AFTER page object, since we are testing this.
#Library    Selenium2Library

*** Test Cases ***

Test Widget Site
    Open Browser  http://www.google.com  phantomjs
    Go To Widget Item Page  category=home-and-garden  id=123
    Title Should Be  Cool Widget
    [Teardown]  Close Widget Item Page
