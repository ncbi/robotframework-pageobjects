*** Settings ***

Documentation  Logging

Library    loggingpage.LoggingPage

*** Test Cases ***

Test Log To File And Screen
    Open LoggingPage
    Log Stuff Only To File  hello world
    [Teardown]  Close Logging Page
