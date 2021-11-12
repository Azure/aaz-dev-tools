

class InvalidSwaggerValueError(ValueError):

    def __init__(self, msg, key, value=None):
        super(InvalidSwaggerValueError, self).__init__()
        self.msg = msg
        self.key = key
        self.value = value

    def __str__(self):
        if self.value:
            return f"{self.__class__.__name__}: {self.msg} : {self.value} : {self.key}"
        else:
            return f"{self.__class__.__name__}: {self.msg} : {self.key}"
