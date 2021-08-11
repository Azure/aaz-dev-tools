import os
import enum
import datetime
import logging

logger = logging.getLogger('backend')


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


class Resource:

    def __init__(self, path, version, file_path, resource_provider):
        self.path = path
        self.version = ResourceVersion(version)
        self.file_path = file_path
        self._resource_provider = resource_provider
        self.file_path_version = self.get_file_path_version(file_path)

    @staticmethod
    def get_file_path_version(file_path):
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
