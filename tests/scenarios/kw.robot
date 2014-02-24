*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    KW

*** Test Cases ***

Test Second Arg is Keyword Arg
    Say Hi To  Mary  frm=Daniel

Test First Arg Is Keyword Arg
    Say Hi To2  frm=Daniel

Test Both Args Are Keyword Args
    Say Hi To3  to=Mary  frm=Daniel
