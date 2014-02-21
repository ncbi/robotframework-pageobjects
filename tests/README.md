Directory for the robot page object project tests.

This directory contains the actual tests written in unittest. The test cases extend `basetestcase.BaseTestCase` which
take care of resetting environment variables, deleting log files, calling the .py or .robot test cases in the
scenarios directory.

The scenarios directory also contains test page objects (in widget.py) which model the mocked widget site under the
`scenarios/pages` directory.
