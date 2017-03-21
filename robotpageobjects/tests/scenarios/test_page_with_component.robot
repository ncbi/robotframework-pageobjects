*** Settings ***

Documentation  Simple test using a page with a component
Library    page_with_component.Page

*** Test Cases ***

Test Widget Site
    Open Page
    [Teardown]  Close Page
