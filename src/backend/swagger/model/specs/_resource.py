import os
import enum
import datetime
import logging
import re

logger = logging.getLogger('backend')


class Resource:

    _CAMEL_CASE_PATTERN = re.compile(r"^([a-zA-Z][a-z0-9]+)(([A-Z][a-z0-9]*)+)$")

    def __init__(self, resource_id, path, version, file_path, resource_provider, body):
        self.path = path
        self.id = resource_id
        self.version = ResourceVersion(version)
        self.file_path = file_path
        self._resource_provider = resource_provider
        self.file_path_version = self._get_file_path_version(file_path)
        operations = {}
        for method, v in body.items():
            if isinstance(v, dict) and 'operationId' in v:
                op_id = self._process_operation_id(v['operationId'], method)
                operations[op_id] = method
        self.operations = operations

        op_group_names = set()
        for op_id in self.operations.keys():
            op_group_name = op_id.strip('_')[0]
            if op_group_name != '':
                op_group_names.add(op_group_name)
        self.op_group_names = op_group_names

    def _process_operation_id(self, op_id, method):
        value = op_id.strip()
        value = value.replace('-', '_')
        if '_' in value:
            return value

        if ' ' in value:
            value = value.replace(' ', '')  # Changed to Camel Case
        match = self._CAMEL_CASE_PATTERN.match(value)
        if not match:
            logger.error(f"InvalidOperationIdFormat:"
                         f"\toperationId should be in format of '[OperationGroupName]_[OperationName]' "
                         f"or '[Verb][OperationGroupName]':\n"
                         f"\tfile: {self.file_path}\n"
                         f"\tpath: {self.path}\n"
                         f"\tmethod: {method} operationId: {op_id}\n")
            return f"_{value}"
        return f"{match[2]}_{match[0]}"    # changed to [OperationGroupName]_[Verb][OperationGroupName]

    @staticmethod
    def _get_file_path_version(file_path):
        dir_path = os.path.dirname(file_path)
        version = os.path.basename(dir_path)
        dir_path = os.path.dirname(dir_path)
        readiness = os.path.basename(dir_path)
        file_path_version = ResourceVersion(version)
        if file_path_version.readiness == ResourceVersion.Readiness.Stable and readiness.lower() != 'stable':
            if readiness not in ('preview', ):
                raise ValueError(f'InvalidReadiness: in file path: {file_path}')
            file_path_version.readiness = ResourceVersion.Readiness.Preview
        return file_path_version


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
