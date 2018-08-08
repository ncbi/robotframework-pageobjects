# Robot Framework Page Objects - Quick Start


## Installation and Setup
Clone this repository to a Linux system, open a terminal in the cloned directory

Verify python is available.

Using pip, install from the requirements.txt file in this directory with:
`$ pip install -r requirements.txt`

Find and download [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads), make sure it is in your path:
`$ which chromedriver`
`/home/aaronpa/chromedriver/chromedriver`

## Running an example
`$ pybot -v baseurl:http://www.conversica.com open_capture.robot`

## Video of Setup and Running
[Screencast video demo](http://screencast.com/t/jhf74SbtYv5) - Note: browser activity not picked up by screen capture, but can be seen live instead of white canvas areas seen in this screen capture.

### What the example does
Starting with the open_capture.robot file, a resource file is read, common.robot. In that file some external library references are defined, as well as the browser type, and browser width and height. The pybot python robot test runner provides for these variables to be overridden via command line - the width of the test run can be changed for each run.

Once the test starts, the browser is opened to the value found in the `baseurl` variable. Selenium will wait for the page to load entirely before proceeding.

The `Startup` and `Shutdown` keywords are defined in common.robot, but not executed. They are called via the Suite Setup and Suite Teardown settings at the stop of open_capture.robot.

After the suite has started and the browser is open and on the intended target, the test logic can begin. In this example test, all links are scraped off of the page using a CSS locator expression. They are then logged from a FOR loop so that the href target for each link is written out. This example test has no assertions and is intended to simply demonstrate the supporting software.

 
