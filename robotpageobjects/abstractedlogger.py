import logging
import sys

from optionhandler import OptionHandler
from context import Context


class Logger(object):
    """Responsible for abstracting Robot logging and logging outside of Robot.
    """

    def __init__(self):
        self.in_robot = Context.in_robot()
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.threshold_level_as_str = self.get_threshold_level_as_str()
        self.threshold_level_as_int = self.get_log_level_from_str(self.threshold_level_as_str)

        # Stream handler is attached from log() since
        # that must be decided at run-time, but here we might as well
        # do the setup to keep log() clean.
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setFormatter(self.formatter)

        # We have to instantiate a logger to something and this is a global
        # logger so we name it by this class. Later in this class'
        # log method, we manipulate the msg string to include the calling
        # page class name.
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(self.threshold_level_as_int)
        fh = logging.FileHandler("po_log.txt", "w")
        fh.setLevel(self.threshold_level_as_int)
        fh.setFormatter(self.formatter)
        logger.addHandler(fh)
        self.logger = logger

    @staticmethod
    def get_threshold_level_as_str():
        ret = OptionHandler(object()).get("log_level") or "INFO"
        return ret.upper()

    @staticmethod
    def get_log_level_from_str(level_as_str):
        """ Convert string log level to integer
        logging level."""

        str_upper = level_as_str.upper()

        try:
            return getattr(logging, str_upper)

        except AttributeError:
            return getattr(logging, "INFO")

    @staticmethod
    def get_normalized_logging_levels(level_as_str, in_robot):
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

        try:
            # Try to get levels from python
            return level_as_str_upper, getattr(logging, level_as_str_upper)
        except AttributeError:
            # Could be user is passing in a Robot log string that
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
        msg = "%s - %s" % (calling_page_name, msg)
        if is_console:
            self.logger.addHandler(self.stream_handler)

        self.logger.log(level_as_int, msg)


