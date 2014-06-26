*** Settings ***

Documentation  Logging

Library    loggingpage.LoggingPage

*** Test Cases ***

Test Log Above Threshold
    Log Debug Is Console False
