Demo
====

This directory contains a demo of the Robot Page Objects package. It demonstrates how you can write a
 readable Robot test leveraging Selenium2Library to create page object libraries, which are usable
in Robot and outside of Robot.

How to run the demo
--------------------

1. Ensure you have phantomjs installed properly on your system.
1. Create a virtual environment, then
1. `pip install robotframework-pageobjects`
1. `$ pybot -vbrowser:firefox -vbaseurl:http://www.ncbi.nlm.nih.gov test_pubmed.txt`

To run the Python unittest example:

1. `$ export PO_BASEURL=http://www.ncbi.nlm.nih.gov`
1. `$ python test_pubmed.py`

By default tests will run in PhantomJS unless you specify otherwise. See the rest of the main README for more features. 
