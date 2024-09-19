import datetime
import enum
import logging
import os
import re

from pluralizer import Pluralizer
from fuzzywuzzy import fuzz

from command.model.configuration import CMDResource
from ._utils import map_path_2_repo
from utils.base64 import b64encode_str, b64decode_str
from swagger.utils import exceptions

logger = logging.getLogger('backend')


class Resource:
    _CAMEL_CASE_PATTERN = re.compile(r"^([a-zA-Z][a-z0-9]+)(([A-Z][a-z0-9]*)+)$")
    _pluralizer = Pluralizer()

    def __init__(self, resource_id, path, version, file_path, resource_provider, body):
        self.path = path
        self.id = resource_id
        self._version = ResourceVersion(version)
        self.file_path = file_path
        self.resource_provider = resource_provider
        self.file_path_version = self._get_file_path_version(file_path)

        operations = {}
        for method, v in body.items():
            if isinstance(v, dict) and 'operationId' in v:
                operations[v['operationId']] = method
        self.operations = operations

    @property
    def version(self):
        return self._version.version
    
    @property
    def rp_name(self):
        return self.resource_provider.name

    def __str__(self):
        return f"{self.path} {self.version}"

    def __hash__(self):
        return hash(f"{self.id} {self.version}")

    def get_operation_group_name(self):
        # TODO: Check database to fetch customized operation group name for resource_id
        if hasattr(self, "_op_group_name"):
            return self._op_group_name

        operation_groups = set()
        for operation_id, method in self.operations.items():
            op_group = self._parse_operation_group_name(operation_id, method)
            operation_groups.add(op_group)

        if None in operation_groups:
            return None

        if len(operation_groups) == 1:
            return operation_groups.pop()

        op_group_name = sorted(
            operation_groups,
            key=lambda nm: fuzz.partial_ratio(self.id, nm),  # use the name which is closest to resource_id
            reverse=True
        )[0]
        setattr(self, "_op_group_name", op_group_name)
        return op_group_name

    def _parse_operation_group_name(self, op_id, method):
        # extract operation group name from operation_id
        value = op_id.strip()
        value = value.replace('-', '_')
        if '_' in value:
            parts = value.split('_')
            op_group_name = parts[0]
            if op_group_name.lower() in ("create", "get", "update", "delete", "patch"):
                op_group_name = parts[1]
        else:
            if ' ' in value:
                value = value.replace(' ', '')  # Changed to Camel Case
            match = self._CAMEL_CASE_PATTERN.match(value)
            if not match:
                logger.error(f"InvalidOperationIdFormat:"
                             f"\toperationId should be in format of '[OperationGroupName]_[OperationName]' "
                             f"or '[Verb][OperationGroupName]':\n"
                             f"\tfile: {map_path_2_repo(self.file_path)}\n"
                             f"\tpath: {self.path}\n"
                             f"\tmethod: {method} operationId: {op_id}\n")
                return None
            op_group_name = match[2]  # [OperationGroupName]

        # Handle plural and singular cases
        words = []
        for part in self.id.split('?')[0].split('/'):
            if part == '{}' and len(words):
                singular = self._pluralizer.singular(words[-1])
                if singular:
                    words[-1] = singular
            else:
                words.append(part.replace('_', ""))
        op_group_singular = self._pluralizer.singular(op_group_name) or op_group_name
        words.reverse()  # search from tail
        for word in words:
            word_singular = self._pluralizer.singular(word) or word
            if len(word_singular) > 1 and op_group_singular.lower().endswith(word_singular.lower()):
                if word == word_singular:
                    # use singular
                    op_group_name = op_group_singular
                elif word != word_singular:
                    # use plural
                    op_group_plural = self._pluralizer.singular(op_group_singular)
                    if op_group_plural is not False:
                        op_group_name = op_group_plural
                break
        return op_group_name

    def _get_file_path_version(self, file_path):
        dir_parts = file_path.split(self.resource_provider.folder_path)[-1].split(os.sep)[:-1]
        dir_parts = [part for part in dir_parts if part]
        if len(dir_parts) < 2:
            raise exceptions.InvalidSwaggerValueError(f"Cannot parse file version", file_path)
        version = None
        for idx in range(len(dir_parts)):
            readiness = dir_parts[idx]
            if readiness.lower() in ('stable', 'preview') and idx + 1 < len(dir_parts):
                version = dir_parts[idx+1]
                break
        if not version:
            raise exceptions.InvalidSwaggerValueError(
                "Cannot parse version and readiness in file path", file_path)
        file_path_version = ResourceVersion(version)
        if file_path_version.readiness == ResourceVersion.Readiness.Stable and readiness.lower() != 'stable':
            if readiness not in ('preview',):
                raise exceptions.InvalidSwaggerValueError(
                    f"Invalid readiness value '{readiness}' in file path", file_path)
            file_path_version.readiness = ResourceVersion.Readiness.Preview
        return file_path_version

    def to_cmd(self, **kwargs):
        resource = CMDResource()
        resource.id = self.id
        resource.version = self.version

        resource.swagger = f"{self.resource_provider}/Paths/{b64encode_str(self.path)}/V/{b64encode_str(self.version)}"
        return resource


class ResourceVersion:
    class Readiness(enum.Enum):
        Preview = 'preview'
        Stable = 'stable'

    def __init__(self, version):
        readiness = self.Readiness.Stable
        for keyword in ('beta', 'preview', 'privatepreview'):
            if keyword in version.lower():
                readiness = self.Readiness.Preview

        self.version = version
        self.readiness = readiness

        self.date = datetime.date.min

        date_piece = version.split('.')[0]  # date is always the prefix of version
        if '-' in date_piece:
            pieces = date_piece.replace('_', '-').split('-')
            try:
                self.date = datetime.date.fromisoformat('-'.join(pieces[:3]))
            except ValueError as err:
                logger.warning(f'ParseVersionDateError: Version={version} : {err}')

    def __str__(self):
        return self.version

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)
