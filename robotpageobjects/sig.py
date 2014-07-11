"""
Responsible for figuring out a method signature as a string.
"""

import inspect
from collections import namedtuple


DefaultArg = namedtuple('DefaultArg', 'is_valid value')

def get_default_arg(args, defaults, i):
    if not defaults:
        return DefaultArg(False, None)

    args_with_no_defaults = len(args) - len(defaults)

    if i < args_with_no_defaults:
        return DefaultArg(False, None)
    else:
        value = defaults[i - args_with_no_defaults]
        if (type(value) is str):
            value = '"%s"' % value
        return DefaultArg(True, value)

def get_method_sig(method):
    argspec = inspect.getargspec(method)
    i=0
    args = []
    for arg in argspec.args:
        default_arg = get_default_arg(argspec.args, argspec.defaults, i)
        if default_arg.is_valid:
            args.append("%s=%s" % (arg, default_arg.value))
        else:
            args.append(arg)
        i += 1
    return "%s(%s)" % (method.__name__, ", ".join(args))

