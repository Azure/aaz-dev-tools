

class InvalidSwaggerValueError(ValueError):

    def __init__(self, msg, key, value, file_path):
        super(InvalidSwaggerValueError, self).__init__(
            f"{self.__class__.__name__}: {msg} : {key}={value} in {file_path}")
