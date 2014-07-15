*** Settings ***

Documentation  Tests negative indexes in Robot keywords, QAR-48165.
...
Library    widget_template.WidgetItemPage
# Keep SE2Lib imported AFTER page object, since we are testing this.
Library    Selenium2Library


*** Test Cases ***

Test Widget Site
    Open Widget Item Page	category=home-and-garden	id=123
    Table Row Should Contain	other-widgets	-1	Useful widget Cube $0.10
    [Teardown]  Close Widget Item Page
