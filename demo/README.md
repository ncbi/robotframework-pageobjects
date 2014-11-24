Demo
====

This directory contains a demo of the Robot Page Objects package. It demonstrates how you can write a
suprememly readable Robot test leveraging Selenium2Library to create page object libraries, which are usable
in Robot and outside of Robot.

How to run the demo
--------------------

1. pip install robotframeworkpageobjects
2. $ pybot -vbrowser:firefox -vbaseurl:http://www.ncbi.nlm.nih.gov test_pubmed.robot

To run the Python unittest example:
$ export PO_BASURL=http://www.ncbi.nlm.nih.gov
$ export PO_BROWSER=firefox
$ python test_pubmed.py

To run the unittest example in Firefox, set the browser environment variable:
$ export PO_BASURL=http://www.google.com
$ export PO_BROWSERL=firefox
$ python test_pubmed.py
