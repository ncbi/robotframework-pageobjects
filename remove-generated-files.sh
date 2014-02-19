#!/bin/bash

find . -name "*.pyc" -exec rm {} \;
find . -name "log.html" -exec rm {} \;
find . -name "output.xml" -exec rm {} \;
find . -name "report.html" -exec rm {} \;
find . -name "*.png" -exec rm {} \;
find . -name "po_log.txt" -exec rm {} \;
find . -name "ghostdriver.log" -exec rm {} \;
