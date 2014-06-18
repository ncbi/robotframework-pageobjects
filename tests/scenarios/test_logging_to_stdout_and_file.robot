*** Settings ***

Documentation  Logging

Library    loggingpage.LoggingPage

*** Test Cases ***

Test Log To File And Screen
    Open Logging Page
    Log Warning  hello world
    [Teardown]  Close Logging Page
