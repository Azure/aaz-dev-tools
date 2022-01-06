from swagger.controller.specs_manager import SwaggerSpecsManager

from utils import exceptions

from flask import Blueprint, jsonify


bp = Blueprint('swagger', __name__, url_prefix='/swagger/specs')


@bp.errorhandler(exceptions.InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict())


# modules
@bp.route("/<plane>", methods=("Get",))
def get_modules_by(plane):
    result = []
    for module in SwaggerSpecsManager.get_modules(plane):
        m = {
            "id": f"{bp.url_prefix}/{module}",
            "name": module.name,
            "folder": module.folder_path,
        }
        result.append(m)
    return jsonify(result)


# resource providers
@bp.route("/<plane>/<path:mod_names>/providers", methods=("Get", ))
def get_resource_providers_by(plane, mod_names):
    result = []
    for rp in SwaggerSpecsManager.get_resource_providers(plane, mod_names):
        result.append({
            "id": f"{bp.url_prefix}/{rp}",
            "name": rp.name,
            "folder": rp.folder_path,
        })
    return jsonify(result)


# resources
@bp.route("/<plane>/<path:mod_names>/providers/<rp_name>/resources", methods=("Get", ))
def get_resources_by(plane, mod_names, rp_name):
    result = []
    rp, resource_op_group_map = SwaggerSpecsManager.get_grouped_resource_map(plane, mod_names, rp_name)
    for op_group_name, resource_map in resource_op_group_map.items():
        for resource_id, version_map in resource_map.items():
            rs = {
                "opGroup": op_group_name,
                "id": resource_id,
                "versions": []
            }
            for version, resource in version_map.items():
                rs['versions'].append({
                    "file": resource.file_path,
                    "version": str(resource.version),
                    "path": resource.path,
                })
            result.append(rs)
    return jsonify(result)

