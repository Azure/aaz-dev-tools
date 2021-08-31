import os
import json
import logging
from swagger.utils import exceptions


logger = logging.getLogger('backend')


class SwaggerLoader:

    def __init__(self):
        self._loaded = {}
        self.loaded_swaggers = []

    def load_swagger(self, file_path):
        from swagger.model.schema.swagger import Swagger
        file_key = f'{file_path}#'
        if file_key in self._loaded:
            return self._loaded[file_key]

        with open(file_path, 'r', encoding='utf-8') as f:
            body = json.load(f)
        if 'example' in file_path.lower():
            self._loaded[file_key] = body
        else:
            self._loaded[file_key] = Swagger(body, file_path=file_path)
            self.loaded_swaggers.append(self._loaded[file_key])

        return self._loaded[file_key]

    def get_swagger(self, file_path):
        file_key = f'{file_path}#'
        return self._loaded.get(file_key, None)

    def load_ref(self, file_path, ref_link):
        path, name = self._parse_ref_link(file_path, ref_link)
        key = f'{path}#{name}'

        if key in self._loaded:
            return self._loaded[key], path, key

        ref = self.get_swagger(path)
        if ref is None:
            try:
                ref = self.load_swagger(path)
            except FileNotFoundError:
                raise exceptions.InvalidSwaggerValueError(
                    msg='Cannot find reference swagger file',
                    key="$ref", value=ref_link, file_path=file_path)

        for prop in name.split('/'):
            if prop == '':
                continue
            try:
                if isinstance(ref, dict):
                    ref = ref[prop]
                else:
                    ref = getattr(ref, prop)
            except (KeyError, AttributeError):
                raise exceptions.InvalidSwaggerValueError(
                    msg='Failed to find reference in swagger',
                    key="$ref", value=ref_link, file_path=file_path)

        assert ref is not None
        self._loaded[key] = ref
        return ref, path, key

    @staticmethod
    def _parse_ref_link(file_path, ref_link):
        parts = ref_link.strip().split('#')

        if not (1 <= len(parts) <= 2):
            raise exceptions.InvalidSwaggerValueError(
                msg="Invalid Reference Value",
                key="$ref", value=ref_link, file_path=file_path)

        if parts[0] == '':
            # start with '#'
            return file_path, parts[1]

        # find ref_file_path
        path = os.path.dirname(file_path)
        for s in parts[0].split('/'):
            if s == '.':
                continue
            elif s == '':
                continue
            elif s == '..':
                path = os.path.dirname(path)
            else:
                path = os.path.join(path, s)

        if len(parts) == 2:
            return path, parts[1]
        else:
            return path, ''
