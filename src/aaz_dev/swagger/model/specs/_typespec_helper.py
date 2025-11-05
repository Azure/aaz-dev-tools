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
        def load_file_lines(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.readlines()

        def parse_by_line(lines):
            namespace, is_mgmt_plane = None, False
            for line in lines:
                if line.startswith("@armProviderNamespace"):
                    is_mgmt_plane = True

                if line.startswith("namespace "):
                    assert namespace is None
                    namespace = re.match(r"^namespace\s+([A-Za-z0-9.]+)", line).group(1)
                    # armProviderNamespace will always be appeared before namespace
                    break

            return namespace, is_mgmt_plane

        def expand(path):
            base = os.path.dirname(path)

            content = []
            for line in lines:
                if match := re.compile(r'^import "([^"]+)"').findall(line):
                    rel_path = match[0]
                    abs_path = os.path.abspath(os.path.join(base, rel_path))

                    if os.path.isfile(abs_path):  # expand first level only; otherwise, may have circular reference
                        with open(abs_path, "r", encoding="utf-8") as f:
                            content.append("".join(f.readlines()))
                    else:
                        content.append(line)
                else:
                    content.append(line)

            return "".join(content).split("\n")

        lines = load_file_lines(path)
        if any("@armProviderNamespace" in line for line in lines):
            namespace, is_mgmt_plane = parse_by_line(lines)

        else:
            namespace, is_mgmt_plane = parse_by_line(expand(path))

        if namespace is None:
            return None, None

        return namespace, is_mgmt_plane
