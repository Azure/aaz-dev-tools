import json
from typing import Dict, Optional


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: None=None, payload: Optional[Dict[str, str]]=None) -> None:
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

    def __str__(self):
        s = f"{self.message}"
        if self.status_code:
            s +=f'\nstatus_code: {self.status_code}'
        if self.payload:
            try:
                s += f'\npayload: {json.dumps(self.payload)}'
            except:
                s += f'\npayload: {self.payload}'
        return s


class VerificationError(InvalidAPIUsage):

    def __init__(self, message: str, details: str, status_code: None=None) -> None:
        super().__init__(message=message, status_code=status_code, payload={
            'details': details
        })


class ResourceNotFind(InvalidAPIUsage):
    status_code = 404


class ResourceConflict(InvalidAPIUsage):
    status_code = 409


