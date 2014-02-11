import re
import os
import imp
try:
    from robot.libraries.BuiltIn import BuiltIn
except ImportError:
    pass


class OptionHandler(object):

    """
    Handles options either from Robot Framework or from
    outside Robot Framework.
    """

    _instance = None
    _opts = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(OptionHandler, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def _get_opts_for_unittest(self):
        ret = {}
        # Trying to call outside Robot Framework
        # Configire with environment variables
        var_file_path = os.environ["VAR_FILE"]
        if var_file_path:
            abs_var_file_path = os.path.abspath(var_file_path)
            try:
                vars_mod = imp.load_source("vars", abs_var_file_path)

            except ImportError, e:
                raise Exception("Couldn't import variable file: %s" % e.message)

            d = vars_mod.__dict__
            for prop in d:
                if not prop.startswith("_"):
                    ret[self._convert_to_robot_format(prop)] = d[prop]
                    
        return ret

    def __init__(self):
        try:
            self._opts = BuiltIn().get_variables()

        except AttributeError:
            self._opts = self._get_opts_for_unittest()

    def _convert_to_robot_format(self, name):
        return name if re.match("\$\{.+\}", name) else "${%s}" % name

    def get(self, name):
        """
        Gets an option value given an option name
        """

        ret = None
        try:
            ret = self._opts[self._convert_to_robot_format(name)]
        except KeyError:
            pass

        return ret

