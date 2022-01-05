from ..model.specs import SwaggerSpecs

from utils import Config, exceptions

from flask import Blueprint, url_for, jsonify, abort, request
from collections import OrderedDict


bp = Blueprint('swagger', __name__, url_prefix='/swagger/specifications')


@bp.errorhandler(exceptions.InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict())


# modules
@bp.route("/<plane>-plane", methods=("Get",))
def get_modules_by(plane):
    specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
    if plane == "mgmt":
        modules = specs.get_mgmt_plane_modules()
    elif plane == "data":
        modules = specs.get_data_plane_modules()
    else:
        raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}-plane'")

    result = OrderedDict()
    for m in modules:
        for resource_provider in m.get_resource_providers():
            module = resource_provider.swagger_module
            if module not in result:
                result[module] = {
                    "id": f"{bp.url_prefix}/{module}",
                    "name": resource_provider.swagger_module.name,
                    "folder_path": resource_provider.swagger_module.folder_path,
                    "providers": [],
                }
            result[module]["providers"].append({
                "id": f"{bp.url_prefix}/{resource_provider}",
                "name": resource_provider.name,
                "folder_path": resource_provider.folder_path,
            })
    result = [*result.values()]
    return jsonify(result)


# resource providers
@bp.route("/<plane>-plane/<path:mod_names>/providers", methods=("Get", ))
def get_resource_providers_by(plane, mod_names):
    specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
    if plane == "mgmt":
        module = specs.get_mgmt_plane_module(*mod_names.split('/'))
    elif plane == "data":
        module = specs.get_data_plane_module(*mod_names.split('/'))
    else:
        raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}-plane'")

    result = []
    for resource_provider in module.get_resource_providers():
        result.append({
            "id": f"{bp.url_prefix}/{resource_provider}",
            "name": resource_provider.name,
            "folder_path": resource_provider.folder_path,
        })


# resources
@bp.route("/<plane>-plane/<path:mod_names>/providers/<rp_name>", methods=("Get", ))
def get_resource_provider(plane, mod_names, rp_name):
    specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
    if plane == "mgmt":
        module = specs.get_mgmt_plane_module(*mod_names.split('/'))
    elif plane == "data":
        module = specs.get_data_plane_module(*mod_names.split('/'))
    else:
        raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}-plane'")

    rp_str = f"/{plane}-plane/{mod_names}/providers/{rp_name}"
    rp = None
    for resource_provider in module.get_resource_providers():
        if str(resource_provider) == rp_str:
            rp = resource_provider
            break

    if rp is None:
        abort(404, description="Resource not found")

    result = {
        "id": f"{bp.url_prefix}/{rp}",
        "name": rp.name,
        "folder_path": rp.folder_path,
        "resources": []
    }
    # rp.get_resource_map()
    return result


# def get_module_map(modules, module_name=None):
#     module_map = {}
#     for module in modules:
#         if module_name and module.name != module_name:
#             continue
#         module_map[module.name] = []
#         for resource_provider in module.get_resource_providers():
#             for resource_id, version_map in resource_provider.get_resource_map().items():
#                 module_map[module.name].append({resource_id: [k.version for k in version_map.keys()]})
#     return module_map
