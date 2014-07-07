""" A monkey patch for uritemplate which doesn't do any url escaping.
"""

import uritemplate
from uritemplate import variables

orig_quote = uritemplate._quote

def expand(template, variables):
    uritemplate._quote = _no_quote
    ret = uritemplate.expand(template, variables)
    uritemplate._quote = orig_quote
    return ret


def _no_quote(value, safe, prefix=None):
    return value
