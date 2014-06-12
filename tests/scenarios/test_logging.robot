*** Settings ***

Documentation  Logging

Library    loggingpage.LoggingPage

*** Test Cases ***

Test Log To File And Screen
    Open LoggingPage
    Log Stuff  hello world
    [Teardown]  Close Logging Page
