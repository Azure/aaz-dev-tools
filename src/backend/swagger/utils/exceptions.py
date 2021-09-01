

class InvalidSwaggerValueError(ValueError):

    def __init__(self, msg, key, value=None):
        if value:
            super(InvalidSwaggerValueError, self).__init__(
                f"{self.__class__.__name__}: {msg} : {key} : {value}")
        else:
            super(InvalidSwaggerValueError, self).__init__(
                f"{self.__class__.__name__}: {msg} : {key}")
