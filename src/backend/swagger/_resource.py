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
        pieces = version.split('-')
        suffix = pieces[3:]
        if len(suffix) == 0:
            readiness = self.Readiness.Stable
        elif len(suffix) == 1 and suffix[0].lower() in ('beta', 'preview', 'privatepreview'):
            readiness = self.Readiness.Preview
        else:
            raise ValueError(f"Invalid Version '{version}'")
        self.version = version
        self.readiness = readiness
        self.date = datetime.date.fromisoformat('-'.join(pieces[:3]))

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
