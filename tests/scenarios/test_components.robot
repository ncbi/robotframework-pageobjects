*** Settings ***
Library    widgetresultpagecomponent.ResultsPage

*** Test Cases ***

Test Component
    Open Results Page
    Item On Results Page Should Cost  2  $17.00
    [teardown]    Close Results Page
