import os
import logging
import re

logger = logging.getLogger('aaz')


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
        if not os.path.isdir(folder):
            return files
        for ts_path, cfg_path in cls._iter_entry_files(folder):
            namespace, is_mgmt_plane = cls._parse_main_tsp(ts_path)
            if not namespace:
                continue
            if not is_mgmt_plane:
                files.append((namespace, ts_path, cfg_path))
        return files

    @classmethod
    def _parse_main_tsp(cls, path):
        def expand(import_path):
            with open(import_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            base = os.path.dirname(import_path)

            content = []
            for line in lines:
                if match := import_pattern.findall(line):
                    rel_path = match[0]
                    abs_path = os.path.abspath(os.path.join(base, rel_path))

                    if os.path.isfile(abs_path):  # expand first level only; otherwise, will impact performance
                        with open(abs_path, "r", encoding="utf-8") as f:
                            content.append("".join(f.readlines()))

                    else:
                        content.append(line)
                else:
                    content.append(line)

            return "".join(content).split("\n")

        import_pattern = re.compile(r'^import "([^"]+)"')

        is_mgmt_plane = False
        namespace = None

        for line in expand(path):
            if line.startswith("@armProviderNamespace"):
                is_mgmt_plane = True
            if line.startswith("namespace "):
                assert namespace is None
                namespace = re.match(r"^namespace\s+([A-Za-z0-9.]+)", line).group(1)
                # armProviderNamespace will always be appeared before namespace
                break
        if namespace is None:
            # logger.warning("Failed to parse main tsp file: %s namespace is not exist.", path)
            return None, None
        return namespace, is_mgmt_plane
