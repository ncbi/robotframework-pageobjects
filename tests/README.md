Directory for the robot page object project tests.

This directory contains the actual tests written in unittest. The test cases extend `basetestcase.BaseTestCase` which
take care of resetting environment variables, deleting log files, calling the .py or .robot test cases in the
scenarios directory. In general each test is executed both in the Robot Framework context and in the unittest context.

- The `scenarios` directory contains the unittests and robot tests which the page object framework tests call in a
subprocess.
- The `pages` directory contains the sample site under test
- The `po` directory continas the page objects which are used to test the functionality of the base page object.
