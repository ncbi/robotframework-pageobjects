*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    Selenium2Library
Library    widget_template.WidgetItemPage

*** Test Cases ***

Test Widget Site
    Open Widget Item Page  category=home-and-garden  id=123
    Title Should Be  Cool Widget
    [Teardown]  Close Widget Item Page
