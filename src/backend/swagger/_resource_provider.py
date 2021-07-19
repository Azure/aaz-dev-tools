from ._utils import map_path_2_repo
import re
import yaml
import os
import logging

logger = logging.getLogger('backend')


class ResourceProvider:

    def __init__(self, name, path, readme_path, swagger_module):
        self._name = name
        self._path = path
        self._readme_path = readme_path
        self._swagger_module = swagger_module

        if readme_path is None:
            logger.warning(f"MissReadmeFile: {self._swagger_module}/{self._name}: {map_path_2_repo(path)}")
        self._tags = None

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
                logger.error(f'ParseYamlFailed: {self._readme_path} {flags}: {err}')
                continue

            files = []
            for file_path in body['input-file']:
                file_path = file_path.replace('$(this-folder)/', '')
                file_path = os.path.join(os.path.dirname(self._readme_path), *file_path.split('/'))
                if not os.path.isfile(file_path):
                    logger.warning(f'FileNotExist: {file_path}')
                    continue
                files.append(file_path)

            tag = piece[2]
            if tag is None:
                tag = ''
            tag = tag.strip()
            if tag not in tags:
                tags[tag] = set()
            tags[tag].union(files)
        return tags





