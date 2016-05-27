import re
import os
import imp
import six

from .context import Context
from .exceptions import VarFileImportErrorError


from robot.libraries.BuiltIn import BuiltIn


class OptionHandler(object):

    """
    Handles options either from Robot Framework or from
    outside Robot Framework.
    """

    _instance = None
    _opts = None
    _new_called = 0

    def __new__(cls, *args, **kwargs):

        # Singleton pattern...
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._new_called += 1

        return cls._instance

    def __init__(self, parent_page):
        self.parent_page = parent_page
        self._opts = {}
        self._in_robot = Context().in_robot()
        if self._new_called == 1:
            self._populate_opts(self._in_robot)

    def __repr__(self):
        return "<robotpageobjects.optionhandler.OptionHandler object at %s: %s>" % (id(self), self._opts)

    def _populate_opts(self, robot=True):
        self._opts.update(getattr(self.parent_page, 'options', {}))
        self._opts.update(self._get_opts_from_var_file())
        self._opts.update(self._get_opts_from_env_vars())
        if robot:
            self._opts.update(self._get_opts_from_robot())

    def _get_opts_from_robot(self):
        ret = {}
        robot_vars = BuiltIn().get_variables()
        for var, val in six.iteritems(robot_vars):
            ret[self._normalize(var)] = val
        return ret

    def _get_opts_from_var_file(self):
        ret = {}
        var_file_path = os.environ.get("PO_VAR_FILE", None)
        if var_file_path:
            abs_var_file_path = os.path.abspath(var_file_path)
            try:
                vars_mod = imp.load_source("vars", abs_var_file_path)

            except (ImportError, IOError) as e:
                raise VarFileImportErrorError(
                    "Couldn't import variable file: %s. Ensure it exists and is importable." % var_file_path)

            var_file_attrs = vars_mod.__dict__
            for vars_mod_attr_name in var_file_attrs:
                if not vars_mod_attr_name.startswith("_"):
                    vars_file_var_value = var_file_attrs[vars_mod_attr_name]
                    ret[self._normalize(vars_mod_attr_name)] = vars_file_var_value
        return ret

    def _get_opts_from_env_vars(self):
        ret = {}
        for env_varname in os.environ:
            if env_varname.startswith("PO_") and env_varname.isupper():
                varname = env_varname[3:]
                ret[self._normalize(varname)] = os.environ.get(env_varname)
        return ret

    def _normalize(self, opts):
        """
        Convert an option keyname to lower-cased robot format, or convert
        all the keys in a dictionary to robot format.
        """
        if isinstance(opts, str):
            name = opts.lower()
            rmatch = re.search("\$\{(.+)\}", name)
            return rmatch.group(1) if rmatch else name
        else:
            # We're dealing with a dict
            return {self._normalize(key): val for (key, val) in six.iteritems(opts)}

    def get(self, name, default=None):
        """
        Gets an option value given an option name
        """

        ret = default
        try:
            if self._in_robot:
                ret = self._opts[self._normalize(name)]
            else:
                ret = self._opts[self._normalize(name.replace(" ", "_"))]
        except KeyError:
            pass
        return ret

