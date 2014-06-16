*** Settings ***

Documentation  Logging

Library    loggingpage.LoggingPage

*** Test Cases ***

Test Log To File And Screen
    Open Logging Page
    Log Stuff To Stdout And File  hello world
    [Teardown]  Close Logging Page
