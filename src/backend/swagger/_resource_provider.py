from ._utils import map_path_2_repo


class ResourceProvider:

    def __init__(self, name, path, readme_path, swagger_module):
        self._name = name
        self._path = path
        self._readme_path = readme_path
        self._swagger_module = swagger_module

        if readme_path is None:
            print(f"MissReadmeFile: {self._swagger_module}/{self._name}: {map_path_2_repo(path)}")

