*** Settings ***
Library    widgetresultpagecomponent.ResultPage

*** Test Cases ***

Test Click Element With Selector
    Open Result Page
    Item On Result Page Should Cost  2  $17.00
    [teardown]    Close Result Page