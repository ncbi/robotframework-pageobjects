Demo
====

This directory contains a demo of the Robot Page Objects package. It demonstrates how you can write a
suprememly readable Robot test leveraging Selenium2Library to create page object libraries, which are usable
in Robot and outside of Robot.

How to run the demos
--------------------

1. Create a virtual environment
2. pip install .
3. activate the virtual environment
4. $ pybot -vbrowser:firefox -vbaseurl:http://www.google.com test_google.robot

To run the Python unittest example:
$ export PO_BASURL=http://www.google.com
$ python test_google.py

To run the unittest example in Firefox, set the browser environment variable:
$ export PO_BASURL=http://www.google.com
$ export PO_BROWSERL=firefox
$ python test_google.py

This demo no longer works in Phantomjs. We plan on fixing that in the future.
