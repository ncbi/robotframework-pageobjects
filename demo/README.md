Demo
====

This directory contains a demo of the Robot Page Objects package. It demonstrates how you can write a
suprememly readable Robot test leveraging Selenium2Library to create page object libraries, which are usable
in Robot and outside of Robot.

How to run the demos
--------------------

Install this package:

# Create a virtual environment
# pip install .

Run the Robot demo:
$ pybot -vbaseurl:http://www.google.com test_google.robot

to run in Firefox:
$ pybot -vbrowser:firefox -vbaseurl:http://www.google.com test_google.robot

To run the Python unittest example:
$ export PO_BASURL=http://www.google.com
$ python test_google.py

To run in Firefox, set the browser environment variable:
$ export PO_BASURL=http://www.google.com
$ export PO_BROWSERL=firefox
$ python test_google.py
