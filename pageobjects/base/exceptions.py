class NoBaseUrlException(AttributeError):
    pass


class NoUrlAttributeException(AttributeError):
    pass


class AbsoluteUrlAttributeException(ValueError):
    pass


class AbsoluteUriTemplateException(ValueError):
    pass


class InvalidUriTemplateVariable(ValueError):
    pass
