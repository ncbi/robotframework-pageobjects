class DuplicateKeyError(ValueError):
    """
    Raised when two selector dictionaries are merged and have a
    duplicate key.
    """
    pass

class KeyOverrideWarning(Warning):
    """
    Raised when a subclass attempts to override a parent's selector
    without using the Override class.
    """
    pass

class SelectorError(Exception):
    """
    Raised when there is a problem with selectors.
    """

class UriResolutionError(ValueError):
    """
    Raised when there is a problem with resolving a uri using a template.
    """

class VarFileImportErrorError(ImportError):
    """
    Raised when a variable file can't be imported
    """
    pass


class MissingSauceOptionError(ValueError):
    """
    Raised when there's a missing sauce option 
    """
    pass


class SauceConnectionError(ValueError):
    """
    Raised when the page object cannot connect to the
    sauce service. Could be invalid username or apikey.
    """
    pass


class KeywordReturnsNoneError(ValueError):
    """
    Raised when a page object keyword does not
    return anything, or returns None.
    """
    pass


class ComponentError(KeyError):
    """
    Raised when there is an issue retrieving instances of a component.
    """
    pass


class PageSelectionError(Exception):
    """Raised when a page object cannot be automatically selected
    as the return value of a method"""
    pass