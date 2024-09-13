import datetime
import json
import logging
import os
import re
from collections import OrderedDict

import yaml

from swagger.utils.tools import swagger_resource_path_to_resource_id
from ._resource import Resource, ResourceVersion
from ._utils import map_path_2_repo

logger = logging.getLogger('backend')


class OpenAPIResourceProvider:

    def __init__(self, name, folder_path, readme_path, swagger_module):
        self.name = name
        self.folder_path = folder_path
        self._readme_path = readme_path
        self.swagger_module = swagger_module

        if readme_path is None:
            logger.warning(f"MissReadmeFile: {self} : {map_path_2_repo(folder_path)}")
        self._tags = None
        self._resource_map = None
        self._ignore_resources = {f'/providers/{self.name}/operations'.lower(), }

    def __str__(self):
        return f'{self.swagger_module}/ResourceProviders/{self.name}'

    def get_resource_map(self, refresh=False):
        if refresh or not self._resource_map:
            resource_map = {}
            for root, dirs, files in os.walk(self.folder_path):
                if 'example' in root:
                    continue
                for file in files:
                    if not file.endswith('.json'):
                        continue
                    file_path = os.path.join(root, file)
                    for resource in self._parse_resources_in_file(file_path):
                        if resource.id in self._ignore_resources:
                            continue
                        if resource.id not in resource_map:
                            resource_map[resource.id] = {}
                        if self._replace_current_resource(
                                curr_resource=resource_map[resource.id].get(resource.version, None),
                                resource=resource
                        ):
                            resource_map[resource.id][resource.version] = resource
            self._resource_map = resource_map
        resource_map = self._resource_map
        return resource_map

    def get_resource_map_by_tag(self, tag):
        resource_map = {}
        if tag not in self.tags:
            logger.error(f"Tag: `{tag}` is not exist")
            return resource_map

        for file_path in self.tags[tag]:
            for resource in self._parse_resources_in_file(file_path):
                if resource.id in self._ignore_resources:
                    continue
                if resource.id not in resource_map:
                    resource_map[resource.id] = {}
                if self._replace_current_resource(
                        curr_resource=resource_map[resource.id].get(resource.version, None),
                        resource=resource
                ):
                    resource_map[resource.id][resource.version] = resource
        return resource_map
    
    @property
    def default_tag(self):
        if self._readme_path is None:
            return None

        with open(self._readme_path, 'r', encoding='utf-8') as f:
            readme = f.read()
        lines = readme.split('\n')
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith('### Basic Information'):
                lines = lines[i+1:]
                break
        latest_tag = None
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith('##'):
                break
            if line.startswith('tag:'):
                latest_tag = line.split(':')[-1].strip()
                break
        return latest_tag

    @property
    def tags(self):
        if self._tags is None:
            self._tags = self._parse_readme_input_file_tags()
        return self._tags

    def _parse_readme_input_file_tags(self):
        tags = {}
        if self._readme_path is None:
            return tags

        with open(self._readme_path, 'r', encoding='utf-8') as f:
            readme = f.read()

        re_yaml = re.compile(
            r'```\s*yaml\s*(.*\$\(\s*tag\s*\)\s*==\s*[\'"]\s*(.*)\s*[\'"].*)?\n((((?!```).)*\n)*)```\s*\n',
            flags=re.MULTILINE)
        for piece in re_yaml.finditer(readme):
            flags = piece[1]
            yaml_body = piece[3]
            if 'input-file' not in yaml_body:
                continue

            try:
                body = yaml.safe_load(yaml_body)
            except yaml.YAMLError as err:
                logger.error(f'ParseYamlFailed: {self} : {self._readme_path} {flags}: {err}')
                continue

            files = []
            for file_path in body['input-file']:
                file_path = file_path.replace('$(this-folder)/', '')
                file_path = os.path.join(os.path.dirname(self._readme_path), *file_path.split('/'))
                if not os.path.isfile(file_path):
                    logger.warning(f'FileNotExist: {self} : {file_path}')
                    continue
                files.append(file_path)

            if len(files):
                tag = piece[2]
                if tag is None:
                    tag = ''
                tag = OpenAPIResourceProviderTag(tag.strip(), self)
                if tag not in tags:
                    tags[tag] = set()
                tags[tag] = tags[tag].union(files)

        tags = [*tags.items()]
        tags.sort(key=lambda item: item[0].date, reverse=True)
        tags = OrderedDict(tags)
        return tags

    def _fetch_latest_tag(self, file_path):
        for tag, file_set in self.tags.items():
            if file_path in file_set:
                return tag
        return None

    def _replace_current_resource(self, curr_resource, resource):
        if curr_resource is None:
            # previous resource with same path and version
            return True

        assert curr_resource.id == resource.id and curr_resource.version == resource.version

        if curr_resource.path != resource.path:
            logger.warning(
                f'SimilarResourcePath: {self} :\n'
                f'\tFile: {map_path_2_repo(curr_resource.file_path)} Path: {curr_resource.path}\n'
                f'\tFile: {map_path_2_repo(resource.file_path)} Path: {resource.path}')

        curr_rs_tag = self._fetch_latest_tag(curr_resource.file_path)
        rs_tag = self._fetch_latest_tag(resource.file_path)

        # resource's file path used in tag has higher priority
        if curr_rs_tag is None and rs_tag is not None:
            return True
        elif curr_rs_tag is not None and rs_tag is None:
            return False

        # resource's file path with larger date has higher priority
        if curr_resource.file_path_version.date is not None and resource.file_path_version.date is not None:
            if curr_resource.file_path_version.date < resource.file_path_version.date:
                return True
            elif curr_resource.file_path_version.date > resource.file_path_version.date:
                return False

        # resource's file path in stable has higher priority
        if curr_resource.file_path_version.readiness != resource.file_path_version.readiness:
            if resource.file_path_version.readiness == ResourceVersion.Readiness.Stable:
                return True
            elif curr_resource.file_path_version == ResourceVersion.Readiness.Stable:
                return False

        # resource's file in latest tag has higher priority
        if curr_rs_tag is not None and rs_tag is not None:
            if rs_tag.date > curr_rs_tag.date:
                return True
            elif curr_rs_tag.date > rs_tag.date:
                return False

        logger.warning(f'DuplicatedResource: {self} :\n'
                       f'\tFile: {map_path_2_repo(curr_resource.file_path)} Path: {curr_resource.path}\n'
                       f'\tFile: {map_path_2_repo(resource.file_path)} Path: {resource.path}')
        return False

    def _parse_resources_in_file(self, file_path):
        resources = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                body = json.load(f)
        except Exception as err:
            logger.error(f'InvalidSwaggerFile: {self} : ParseJsonFailed: {file_path} : {err}')
            return resources

        # check swagger version
        swagger_version = body.get('swagger', None)
        if swagger_version != '2.0':
            logger.error(f'InvalidSwaggerFile: {self} : invalid swagger version {swagger_version} in file {file_path}')
            return resources

        # fetch api-version
        info = body.get('info', {})
        version = info.get('version', None)
        if not version:
            logger.error(f'InvalidSwaggerFile: {self} : invalid info version {version} in file {file_path}')

        for path, value in body.get('paths', {}).items():
            resource = Resource(
                resource_id=swagger_resource_path_to_resource_id(path),
                path=path, version=version, file_path=file_path, resource_provider=self, body=value)
            resources.append(resource)

        # x-ms-paths:
        #   alternative to Paths Object that allows Path Item Object to have query parameters for non pure REST APIs
        for path, value in body.get('x-ms-paths', {}).items():
            resource = Resource(
                resource_id=swagger_resource_path_to_resource_id(path),
                path=path, version=version, file_path=file_path, resource_provider=self, body=value)
            resources.append(resource)

        return resources


class OpenAPIResourceProviderTag:

    def __init__(self, tag, resource_provider):
        self._tag = tag
        self.date = None

        if self._tag is not None:
            dt_re = re.compile(r'([0-9]{4})([-_]([0-9]{1,2})([-_]([0-9]{1,2}))?)?')
            try:
                pieces = next(dt_re.finditer(self._tag))
                year = int(pieces[1])
                month = int(pieces[3]) if pieces[3] else 1
                day = int(pieces[5]) if pieces[5] else 1
                self.date = datetime.date(year, month, day)
            except (StopIteration, ValueError):
                logger.warning(f'ParseTagDateError: {resource_provider} : {self._tag}')
                self.date = datetime.date.min

    def __str__(self):
        return self._tag

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)


class TypeSpecResourceProvider:

    def __init__(self, name, entry_files, swagger_module):
        self.name = name
        self.entry_files = entry_files
        self.swagger_module = swagger_module

    def __str__(self):
        return f'{self.swagger_module}/ResourceProviders/{self.name}'
