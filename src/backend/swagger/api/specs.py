from base64 import urlsafe_b64encode, urlsafe_b64decode

from flask import Blueprint, jsonify
from swagger.controller.specs_manager import SwaggerSpecsManager
from utils import exceptions

bp = Blueprint('swagger', __name__, url_prefix='/swagger/specs')


def b64encode_str(value):
    return urlsafe_b64encode(value.encode()).decode()


def b64decode_str(value):
    return urlsafe_b64decode(value).decode()


@bp.errorhandler(exceptions.InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code


# modules
@bp.route("/<plane>", methods=("Get",))
def get_modules_by(plane):
    result = []
    for module in SwaggerSpecsManager.get_modules(plane):
        m = {
            "url": f"{bp.url_prefix}/{module}",
            "name": module.name,
            "folder": module.folder_path,
        }
        result.append(m)
    return jsonify(result)


@bp.route("/<plane>/<path:mod_names>", methods=("Get",))
def get_module(plane, mod_names):
    module = SwaggerSpecsManager.get_module(plane, mod_names)
    result = {
        "url": f"{bp.url_prefix}/{module}",
        "name": module.name,
        "folder": module.folder_path,
        "resourceProviders": []
    }
    for rp in SwaggerSpecsManager.get_resource_providers(plane, mod_names):
        result['resourceProviders'].append({
            "url": f"{bp.url_prefix}/{rp}",
            "name": rp.name,
            "folder": rp.folder_path,
        })
    return jsonify(result)


# resource providers
@bp.route("/<plane>/<path:mod_names>/resource-providers", methods=("Get",))
def get_resource_providers_by(plane, mod_names):
    result = []
    for rp in SwaggerSpecsManager.get_resource_providers(plane, mod_names):
        result.append({
            "url": f"{bp.url_prefix}/{rp}",
            "name": rp.name,
            "folder": rp.folder_path,
        })
    return jsonify(result)


@bp.route("/<plane>/<path:mod_names>/resource-providers/<rp_name>", methods=("Get",))
def get_resource_provider(plane, mod_names, rp_name):
    rp = SwaggerSpecsManager.get_resource_provider(plane, mod_names, rp_name)
    result = {
        "url": f"{bp.url_prefix}/{rp}",
        "name": rp.name,
        "folder": rp.folder_path,
        "resources": []
    }
    resource_op_group_map = SwaggerSpecsManager.get_grouped_resource_map(plane, mod_names, rp_name)
    for op_group_name, resource_map in resource_op_group_map.items():
        for resource_id, version_map in resource_map.items():

            rs_id = f"{bp.url_prefix}/{rp}/resources/{b64encode_str(resource_id)}"
            rs = {
                "opGroup": op_group_name,
                "url": rs_id,
                "id": resource_id,
                "versions": []
            }
            for version, resource in version_map.items():
                version = str(resource.version)
                rs['versions'].append({
                    "url": f"{rs_id}/v/{b64encode_str(version)}",
                    "version": version,
                    "file": resource.file_path,
                    "path": resource.path,
                    "operations": resource.operations
                })
            result['resources'].append(rs)
    return jsonify(result)


# resources
@bp.route("/<plane>/<path:mod_names>/resource-providers/<rp_name>/resources", methods=("Get",))
def get_resources_by(plane, mod_names, rp_name):
    result = []
    rp = SwaggerSpecsManager.get_resource_provider(plane, mod_names, rp_name)
    resource_op_group_map = SwaggerSpecsManager.get_grouped_resource_map(plane, mod_names, rp_name)
    for op_group_name, resource_map in resource_op_group_map.items():
        for resource_id, version_map in resource_map.items():
            rs_url = f"{bp.url_prefix}/{rp}/resources/{b64encode_str(resource_id)}"
            rs = {
                "url": rs_url,
                "opGroup": op_group_name,
                "id": resource_id,
                "versions": []
            }
            for version, resource in version_map.items():
                version = str(resource.version)
                rs['versions'].append({
                    "url": f"{rs_url}/v/{b64encode_str(version)}",
                    "id": resource_id,
                    "version": version,
                    "file": resource.file_path,
                    "path": resource.path,
                    "operations": resource.operations
                })
            result.append(rs)
    return jsonify(result)


# resource
@bp.route("/<plane>/<path:mod_names>/resource-providers/<rp_name>/resources/<resource_id>", methods=("Get",))
def get_resource_in_rp(plane, mod_names, rp_name, resource_id):
    resource_id = b64decode_str(resource_id)
    version_map = SwaggerSpecsManager.get_resource_version_map(
        plane=plane, mod_names=mod_names, resource_id=resource_id, rp_name=rp_name
    )
    rp = list(version_map.values())[0].resource_provider
    op_group_name = SwaggerSpecsManager.get_resource_op_group_name(version_map)
    rs_url = f"{bp.url_prefix}/{rp}/resources/{b64encode_str(resource_id)}"
    result = {
        "url": rs_url,
        "opGroup": op_group_name,
        "id": resource_id,
        "versions": []
    }
    for version, resource in version_map.items():
        version = str(resource.version)
        result['versions'].append({
            "url": f"{rs_url}/v/{b64encode_str(version)}",
            "id": resource_id,
            "version": version,
            "file": resource.file_path,
            "path": resource.path,
            "operations": resource.operations
        })
    return jsonify(result)


@bp.route("/<plane>/<path:mod_names>/resources/<resource_id>", methods=("Get",))
def get_resource_in_module(plane, mod_names, resource_id):
    resource_id = b64decode_str(resource_id)
    version_map = SwaggerSpecsManager.get_resource_version_map(
        plane=plane, mod_names=mod_names, resource_id=resource_id
    )
    rp = list(version_map.values())[0].resource_provider
    op_group_name = SwaggerSpecsManager.get_resource_op_group_name(version_map)
    rs_url = f"{bp.url_prefix}/{rp}/resources/{b64encode_str(resource_id)}"
    result = {
        "url": rs_url,
        "opGroup": op_group_name,
        "id": resource_id,
        "versions": []
    }
    for version, resource in version_map.items():
        version = str(resource.version)
        result['versions'].append({
            "url": f"{rs_url}/v/{b64encode_str(version)}",
            "id": resource_id,
            "version": version,
            "file": resource.file_path,
            "path": resource.path,
            "operations": resource.operations
        })
    return jsonify(result)


# resource version
@bp.route("/<plane>/<path:mod_names>/resource-providers/<rp_name>/resources/<resource_id>/v/<version>",
          methods=("Get",))
def get_resource_version_in_rp(plane, mod_names, rp_name, resource_id, version):
    resource_id = b64decode_str(resource_id)
    version = b64decode_str(version)
    resource = SwaggerSpecsManager.get_resource_in_version(
        plane=plane, mod_names=mod_names, rp_name=rp_name, resource_id=resource_id, version=version
    )
    version = str(resource.version)
    result = {
        "url": f"{bp.url_prefix}/{resource.resource_provider}/resources/"
               f"{b64encode_str(resource.id)}/v/{b64encode_str(version)}",
        "id": resource_id,
        "version": version,
        "file": resource.file_path,
        "path": resource.path,
        "operations": resource.operations
    }
    return jsonify(result)


@bp.route("/<plane>/<path:mod_names>/resources/<resource_id>/v/<version>", methods=("Get",))
def get_resource_version_in_module(plane, mod_names, resource_id, version):
    resource_id = b64decode_str(resource_id)
    version = b64decode_str(version)
    resource = SwaggerSpecsManager.get_resource_in_version(
        plane=plane, mod_names=mod_names, resource_id=resource_id, version=version
    )
    version = str(resource.version)
    result = {
        "url": f"{bp.url_prefix}/{resource.resource_provider}/resources/"
               f"{b64encode_str(resource.id)}/v/{b64encode_str(version)}",
        "id": resource_id,
        "version": version,
        "file": resource.file_path,
        "path": resource.path,
        "operations": resource.operations
    }
    return jsonify(result)
