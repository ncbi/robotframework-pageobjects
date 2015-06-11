*** Settings ***
Library  Selenium2Library
Library  widget_rel_uri_attr.Page

*** Test Cases ***

Overridden Keyword Should Be Available in Se2Lib
    Open Browser  ${BASEURL}/site/index.html  phantomjs
    Title Should Be  Widget Homepage
    [teardown]  Close Browser