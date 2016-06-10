Directory for the robot page object project tests.

This directory contains the actual tests written in unittest. The test cases extend `basetestcase.BaseTestCase` which
take care of resetting environment variables, deleting log files, calling the .py or .robot test cases in the
scenarios directory. In general each functional test is executed both in the Robot Framework context and in the
unittest context. Functional tests are found in functional.py. They run actual browsers. Unittests are found in unit
.py and test simple inputs and outputs of critical page object methods and helpers.

- The `scenarios` directory contains the unittests and robot tests which the page object framework tests call in a
subprocess.
- The `site` directory contains the sample site under test
- The `po` directory continas the page objects which are used to test the functionality of the base page object.
