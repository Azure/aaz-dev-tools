import os
import logging

logger = logging.getLogger('backend')


class TypeSpecHelper:

    @staticmethod
    def _iter_entry_files(folder):
        if not os.path.isdir(folder):
            raise ValueError(f"Path not exist: {folder}")
        ts_path = os.path.join(folder, "main.tsp")
        cfg_path = os.path.join(folder, "tspconfig.yaml")
        if os.path.isfile(ts_path) and os.path.isfile(cfg_path):
            yield ts_path, cfg_path
        for root, dirs, files in os.walk(folder):
            ts_path = os.path.join(root, "main.tsp")
            cfg_path = os.path.join(root, "tspconfig.yaml")
            if os.path.isfile(ts_path) and os.path.isfile(cfg_path):
                yield ts_path, cfg_path

    @classmethod
    def find_mgmt_plane_entry_files(cls, folder):
        files = []
        for ts_path, cfg_path in cls._iter_entry_files(folder):
            namespace, is_mgmt_plane = cls._parse_main_tsp(ts_path)
            if is_mgmt_plane:
                files.append((namespace, ts_path, cfg_path))
        return files

    @classmethod
    def find_data_plane_entry_files(cls, folder):
        files = []
        for ts_path, cfg_path in cls._iter_entry_files(folder):
            namespace, is_mgmt_plane = cls._parse_main_tsp(ts_path)
            if not namespace:
                continue
            if not is_mgmt_plane:
                files.append((namespace, ts_path, cfg_path))
        return files

    @classmethod
    def _parse_main_tsp(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        is_mgmt_plane = False
        namespace = None
        for line in lines:
            if line.startswith("@armProviderNamespace"):
                is_mgmt_plane = True
            if line.startswith("namespace "):
                assert namespace is None
                namespace = line.split(' ')[1].strip()
                # armProviderNamespace will always be appeared before namespace
                break
        if namespace is None:
            # logger.warning("Failed to parse main tsp file: %s namespace is not exist.", path)
            return None, None
        return namespace, is_mgmt_plane
