class DuplicateKeyException(ValueError):
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


class NoBaseUrlException(AttributeError):
    """
    Raised when no baseurl is set for the page object. A baseurl
    must always be set and url/uri_template attributes must be relative
    URIs.
    """
    pass


class NoUriAttributeException(AttributeError):
    """
    Raised when nothing is passed to a page object's open method
    but no url attribute is set on the page object.
    """
    pass


class AbsoluteUriAttributeException(ValueError):
    """
    Raised when nothing is passed to a page object's open
    method and the page object's `url` attribute is set to an
    absolute URL.
    """
    pass


class AbsoluteUriTemplateException(ValueError):
    """
    Raised when a uri_template attribute on a page object is
    set to an absolute URL.
    """
    pass


class InvalidUriTemplateVariableException(ValueError):
    """
    Raised when a variable passed to a page object's open
    method doesn't match a variable in the page object's
    `uri_template` attribute.
    """
    pass


class VarFileImportErrorException(ImportError):
    """
    Raised when a variable file can't be imported
    """
    pass


class MissingSauceOptionException(ValueError):
    """
    Raised when there's a missing sauce option 
    """
    pass
