

class InvalidSwaggerValueError(ValueError):

    def __init__(self, msg, key, value=None):
        # from swagger.model.specs._utils import map_path_2_repo
        # key = [map_path_2_repo(key[0]), *key[1:]]
        if value:
            super(InvalidSwaggerValueError, self).__init__(
                f"{self.__class__.__name__}: {msg} : {key} : {value}")
        else:
            super(InvalidSwaggerValueError, self).__init__(
                f"{self.__class__.__name__}: {msg} : {key}")
