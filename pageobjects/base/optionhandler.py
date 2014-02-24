import re
import os
import imp
from context import Context
from robot.conf import RobotSettings
from robot.variables import GLOBAL_VARIABLES, init_global_variables

# Our page objects should be used independently of Robot Framework
try:
    from robot.libraries.BuiltIn import BuiltIn
except ImportError:
    pass


# Set up Robot's global variables so we get all the built-in default settings when we're outside Robot.
# We need this for Selenium2Library's _get_log_dir() method, among other things.
# TODO: DCLT-693: Put this handling in some other place.
# TODO: DCLT-659: Write test, confirm we're not breaking anything inside Robot, and that we are
#  not preventing the setting of certain CL options. We shouldn't be, since we use _get_opts_no_robot() below,
#  and then fall back if needed to GLOBAL_VARIABLES, which will always have Robot's default values.
if not Context.in_robot():
    init_global_variables(RobotSettings())


class OptionHandler(object):

    """
    Handles options either from Robot Framework or from
    outside Robot Framework.
    """

    _instance = None
    _opts = {}
    _new_called = 0

    def __new__(cls, *args, **kwargs):

        # Singleton pattern...
        if cls._instance is None:
            cls._instance = super(OptionHandler, cls).__new__(cls, *args, **kwargs)
            cls._new_called += 1

        return cls._instance

    def __init__(self):

        if self._new_called == 1:
            try:
                self._opts = BuiltIn().get_variables()
            except AttributeError:
                self._opts = {}
                self._opts.update(self._get_opts_no_robot())

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
        var_file_path = os.environ.get("PO_VAR_FILE", None)
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
                    ret[self._normalize(vars_mod_attr_name)] = vars_file_var_value

        # After configs are saved from var file, get individual environment variables
        for env_varname in os.environ:
            if env_varname.startswith("PO_"):
                varname = env_varname[3:]
                ret[self._normalize(varname)] = os.environ.get(env_varname)

        return ret

    def _normalize(self, opts):
        """
        Convert an option keyname to lower-cased robot format, or convert
        all the keys in a dictionary to robot format.
        """
        if isinstance(opts, basestring):
            name = opts.lower()
            return name if re.match("\$\{.+\}", name) else "${%s}" % name
        else:
            # We're dealing with a dict
            return {self._normalize(key): val for (key, val) in opts.iteritems()}

    def get(self, name):
        """
        Gets an option value given an option name
        """

        ret = None
        try:
            if Context.in_robot():
                ret = self._opts[self._normalize(name)]
            else:
                ret = self._opts[self._normalize(name.replace(" ", "_"))]
        except KeyError:
            pass

        return ret

