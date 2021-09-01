

class InvalidSwaggerValueError(ValueError):

    def __init__(self, msg, key, value):
        if isinstance(key, list):
            key = '__'.join(key)
        super(InvalidSwaggerValueError, self).__init__(
            f"{self.__class__.__name__}: {msg} : {key} : {value}")
