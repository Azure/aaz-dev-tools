from ..model.specs import SwaggerSpecs
import os

swagger_path = os.environ['SWAGGER_PATH']

def get_module_map(modules, module_name=None):
        module_map = {}
        for module in modules:
            if module_name and module.name != module_name:
                continue
            module_map[module.name] = []
            for resource_provider in module.get_resource_providers():
                for resource_id, version_map in resource_provider.get_resource_map().items():
                    module_map[module.name].append({resource_id: [k.version for k in version_map.keys()]})
        return module_map


def generate_specs():
    specs = SwaggerSpecs(folder_path=swagger_path)
    mgmt_plane_modules = specs.get_mgmt_plane_modules()
    data_plane_modules = specs.get_data_plane_modules()

    mgmt_plane_map = get_module_map(mgmt_plane_modules)
    data_plane_map = get_module_map(data_plane_modules)
    return {"mgmt":mgmt_plane_map, "data": data_plane_map}


def get_specs_for_module(module_name):
    specs = SwaggerSpecs(folder_path=swagger_path)
    mgmt_plane_modules = specs.get_mgmt_plane_modules()
    data_plane_modules = specs.get_data_plane_modules()

    mgmt_plane_map = get_module_map(mgmt_plane_modules, module_name)
    data_plane_map = get_module_map(data_plane_modules, module_name)
    return {"mgmt":mgmt_plane_map, "data": data_plane_map}