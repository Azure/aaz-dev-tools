class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class VerificationError(InvalidAPIUsage):

    def __init__(self, message, details, status_code=None):
        super().__init__(message=message, status_code=status_code, payload={
            'details': details
        })


class ResourceNotFind(InvalidAPIUsage):
    status_code = 404


class ResourceConflict(InvalidAPIUsage):
    status_code = 409


