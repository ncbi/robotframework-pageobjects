from basetestcase import BaseTestCase
from robot.api import logger


class TestUnitTest(BaseTestCase):

    def test_unittest_defaults(self):
        run = self.run_program("python test_unittest.py")
        self.assert_run(run, expected_run_status="OK")
        import logging
        logger = logging.getLogger("robot.api.logger")




