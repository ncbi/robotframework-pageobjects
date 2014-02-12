import re
import os
import imp

# Our page objects should be used independently of Robot Framework
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

    def __init__(self):
        try:
            self._opts = BuiltIn().get_variables()

        except AttributeError:
            self._opts = self._get_opts_no_robot()

    def _get_opts_no_robot(self):

        """
        Options for tests written outside Robot Framework
        are gotten by

        1) a python module that exposes variables,
        just like Robot. We look for an environment variable called
        PO_VAR_FILE which should point to that module.

        2) Individual environment variables, eg. PO_BROWSER. Individual
        env vars override those set in file pointed to by "PO_VAR_FILE"
        """
        ret = {}
        # Trying to call outside Robot Framework
        # Configire with environment variables
        var_file_path = os.environ["PO_VAR_FILE"]
        if var_file_path:
            abs_var_file_path = os.path.abspath(var_file_path)
            try:
                vars_mod = imp.load_source("vars", abs_var_file_path)

            except ImportError, e:
                raise Exception("Couldn't import variable file: %s" % e.message)

            var_file_attrs = vars_mod.__dict__
            for vars_mod_attr_name in var_file_attrs:
                if not vars_mod_attr_name.startswith("_"):
                    vars_file_var_value = var_file_attrs[vars_mod_attr_name]
                    ret[self._convert_to_robot_format(vars_mod_attr_name)] = vars_file_var_value

        # After configs are saved from var file, get individual environment variables
        for env_varname in os.environ:
            if env_varname.startswith("PO_"):
                varname = env_varname[3:].lower()
                ret[self._convert_to_robot_format(varname)] = os.environ.get(env_varname)

        return ret

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

