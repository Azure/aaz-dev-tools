import json
import logging
import os
from collections import OrderedDict

from swagger.utils import exceptions

logger = logging.getLogger('backend')


class SwaggerLoader:

    def __init__(self):
        self._loaded = {}
        self.loaded_swaggers = OrderedDict()
        self._linked_idx = 0

    def load_file(self, file_path):
        from swagger.model.schema.swagger import Swagger
        loaded = self.get_loaded(file_path)
        if loaded is not None:
            return loaded

        with open(file_path, 'r', encoding='utf-8') as f:
            body = json.load(f)

        if 'example' in file_path.lower():
            loaded = body
        else:
            self.patch_swagger(body)
            loaded = Swagger(body)
            self.loaded_swaggers[file_path] = loaded
        self._cache_loaded(loaded, file_path)
        return loaded

    @staticmethod
    def patch_swagger(body):
        """Current will patch `additionalProperties: {}` expression"""
        def _patch_list(lst):
            for item in lst:
                if isinstance(item, dict):
                    _patch_dict(item)

        def _patch_dict(dct):
            for key in [*dct.keys()]:
                if key == "additionalProperties" and dct[key] == {}:
                    # replace `additionalProperties: {}` by `additionalProperties: true`
                    dct[key] = True
                _patch(dct[key])

        def _patch(data):
            if isinstance(data, dict):
                _patch_dict(data)
            elif isinstance(data, list):
                _patch_list(data)

        _patch(body)

    def link_swaggers(self):
        while self._linked_idx < len(self.loaded_swaggers):
            file_path, swagger = [*self.loaded_swaggers.items()][self._linked_idx]
            swagger.link(self, file_path)
            self._linked_idx += 1

    def get_loaded(self, *traces):
        return self._loaded.get(traces, None)

    def _cache_loaded(self, loaded, *traces):
        self._loaded[traces] = loaded

    def load_ref(self, ref_link, *ref_traces):
        traces = self._parse_ref_link(ref_traces, ref_link)

        ref = self.get_loaded(*traces)
        if ref is not None:
            return ref, traces

        file_path = traces[0]
        ref = self.get_loaded(file_path)
        if ref is None:
            try:
                ref = self.load_file(file_path)
            except FileNotFoundError:
                raise exceptions.InvalidSwaggerValueError(
                    msg='Cannot find reference swagger file',
                    key=ref_traces, value=ref_link)

        for prop in traces[1:]:
            assert prop != ''
            try:
                if isinstance(ref, dict):
                    ref = ref[prop]
                elif isinstance(ref, list):
                    ref = ref[prop]
                else:
                    ref = getattr(ref, prop)
            except (KeyError, AttributeError):
                raise exceptions.InvalidSwaggerValueError(
                    msg='Failed to find reference in swagger',
                    key=ref_traces, value=ref_link)

        assert ref is not None
        self._cache_loaded(ref, *traces)
        return ref, traces

    @classmethod
    def _parse_ref_link(cls, ref_traces, ref_link):
        file_path = ref_traces[0]

        parts = ref_link.strip().split('#')

        if not (1 <= len(parts) <= 2):
            raise exceptions.InvalidSwaggerValueError(
                msg="Invalid Reference Value",
                key=ref_traces, value=ref_link)

        if parts[0] == '':
            # start with '#'
            traces = [trace for trace in parts[1].split('/') if trace]
            return file_path, *traces

        # find ref_file_path
        file_path = os.path.dirname(file_path)
        for s in parts[0].split('/'):
            if s == '.':
                continue
            elif s == '':
                continue
            elif s == '..':
                file_path = os.path.dirname(file_path)
            else:
                file_path = os.path.join(file_path, s)
        if len(parts) == 2:
            traces = [trace for trace in parts[1].split('/') if trace]
            return file_path, *traces
        else:
            return file_path,
