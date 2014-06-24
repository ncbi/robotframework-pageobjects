import logging
import sys
import robot.api.logger
import robot.output.pyloggingconf as robot_logging_conf

from optionhandler import OptionHandler
from context import Context


class Logger(object):
    """Responsible for abstracting Robot logging and logging outside of
    Robot.
    """
    in_robot = Context.in_robot()
    _instance = None
    threshold_level_as_str = OptionHandler().get("log_level") or "INFO"
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def __new__(cls, *args, **kwargs):
        """
        Make this object a singleton. We're using this in optionhandler as well,
        so we should probably create a decorator. I'm surprised Python doesn't
        provide one. Alternatively we could just make everything class methods
        on this class.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self.threshold_level_as_str = self.threshold_level_as_str.upper()
        self._threshold_level_as_int = self.get_log_level_from_str(self.threshold_level_as_str)
        if self.in_robot:
            self.logger = robot.api.logger
        else:
            # Stream handler is attached from log() since
            # that must be decided at run-time, but here we might as well
            # do the setup to keep log() clean.
            self.stream_handler = logging.StreamHandler(sys.stdout)
            self.stream_handler.setFormatter(self.formatter)
            logger = logging.getLogger(self.__class__.__name__)
            logger.setLevel(self._threshold_level_as_int)
            fh = logging.FileHandler("po_log.txt", "w")
            fh.setLevel(self._threshold_level_as_int)
            fh.setFormatter(self.formatter)
            logger.addHandler(fh)
            logger._attached_sh = False
            self.logger = logger

    def get_log_level_from_str(self, str):
        """ Convert string log level to integer
        logging level."""

        str_upper = str.upper()

        try:
            return getattr(logging, str_upper)

        except AttributeError:
            return getattr(logging, self._default_level_to_log)

    def _get_logger(self):
        if self.in_robot:
            ret = robot.api.logger

        else:
            ret = self._get_logger_outside_robot()

        return ret

    def get_normalized_logging_levels(self, level_as_str, in_robot):
        """ Given a log string, returns the translated log level string and the translated
        python logging level integer. This is needed because there are logging level
        constants defined in Robot that are not in Python, and Python logging level
        constants that are not defined in Robot.
        """

        translation_map = {
            "CRITICAL": "WARN",
            "WARNING": "WARN",
            "NOTSET": "TRACE"
        }

        level_as_str_upper = level_as_str.upper()
        translated_level_str = None
        if in_robot:
            robot_levels = robot_logging_conf.LEVELS

            # The level passed in is a Robot level, so look up corresponding
            # python integer logging level
            if level_as_str_upper is "WARNING":
                # There is no "WARNING" in Robot
                level_as_str_upper = "WARN"

            if level_as_str_upper in robot_levels:
                return level_as_str_upper, robot_levels[level_as_str_upper]
            else:
                # The level passed-in doesn't correspond to a
                # Robot level, so translate it to one, then look it up.

                try:
                    translated_level_str = translation_map[level_as_str_upper]
                except KeyError:
                    raise ValueError("The log level '%s' is invalid" % level_as_str_upper)
                return translated_level_str, robot_levels[translated_level_str]

        else:
            try:
                # Try to get levels from python
                return level_as_str_upper, getattr(logging, level_as_str_upper)
            except AttributeError:
                # Woops, could be user is passing in a Robot log string that
                # doesn't exist for Python. So look up the Python level given the robot level
                inv_translation_map = {v: k for k, v in translation_map.items()}

                try:
                    translated_level_str = inv_translation_map[level_as_str_upper]
                except KeyError:
                    translated_level_str = level_as_str_upper
                try:
                    return translated_level_str, getattr(logging, translated_level_str)
                except AttributeError:
                    raise ValueError("The log level '%s' is invalid" % level_as_str_upper)



    def log(self, msg, calling_page_name, level="INFO", is_console=True):
        level_as_str, level_as_int = self.get_normalized_logging_levels(level, self.in_robot)
        msg  = "%s - %s" %(calling_page_name, msg)
        if self.in_robot:
            self.logger.write(msg, level_as_str)
            if is_console:
                # Robot's logging only outputs to stdout if it's a warning, so allow
                # always logging to console, unless caller specifies not to.
                robot.api.logger.console("%s - %s" %(level, msg))
        else:
            if is_console:
                self.logger.addHandler(self.stream_handler)

            self.logger.log(level_as_int, msg)

"""
l = Logger()
l.log("foo bar", "FooPage", is_console=False)
l.log("ta ta", "BarPage")

"""


