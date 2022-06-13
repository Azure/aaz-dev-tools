from flask import Blueprint, jsonify, url_for

from swagger.controller.specs_manager import SwaggerSpecsManager

bp = Blueprint('swagger', __name__, url_prefix='/Swagger/Specs')


# modules
@bp.route("/<plane>", methods=("GET",))
def get_modules_by(plane):
    specs_manager = SwaggerSpecsManager()
    result = []
    for module in specs_manager.get_modules(plane):
        m = {
            "url": url_for('swagger.get_module', plane=plane, mod_names=module.names),
            "name": module.name,
            "folder": module.folder_path,
        }
        result.append(m)
    return jsonify(result)


@bp.route("/<plane>/<list_path:mod_names>", methods=("GET",))
def get_module(plane, mod_names):
    specs_manager = SwaggerSpecsManager()
    module = specs_manager.get_module(plane, mod_names)
    result = {
        "url": url_for('swagger.get_module', plane=plane, mod_names=mod_names),
        "name": module.name,
        "folder": module.folder_path,
        "resourceProviders": []
    }
    for rp in specs_manager.get_resource_providers(plane, mod_names):
        result['resourceProviders'].append({
            "url": url_for('swagger.get_resource_provider', plane=plane, mod_names=mod_names, rp_name=rp.name),
            "name": rp.name,
            "folder": rp.folder_path,
        })
    return jsonify(result)


# resource providers
@bp.route("/<plane>/<list_path:mod_names>/ResourceProviders", methods=("GET",))
def get_resource_providers_by(plane, mod_names):
    specs_manager = SwaggerSpecsManager()
    result = []
    for rp in specs_manager.get_resource_providers(plane, mod_names):
        result.append({
            "url": url_for('swagger.get_resource_provider', plane=plane, mod_names=mod_names, rp_name=rp.name),
            "name": rp.name,
            "folder": rp.folder_path,
        })
    return jsonify(result)


@bp.route("/<plane>/<list_path:mod_names>/ResourceProviders/<rp_name>", methods=("GET",))
def get_resource_provider(plane, mod_names, rp_name):
    specs_manager = SwaggerSpecsManager()
    rp = specs_manager.get_resource_provider(plane, mod_names, rp_name)
    result = {
        "url": url_for('swagger.get_resource_provider', plane=plane, mod_names=mod_names, rp_name=rp.name),
        "name": rp.name,
        "folder": rp.folder_path,
        "resources": []
    }
    resource_op_group_map = specs_manager.get_grouped_resource_map(plane, mod_names, rp_name)
    for op_group_name, resource_map in resource_op_group_map.items():
        for resource_id, version_map in resource_map.items():
            rs = {
                "opGroup": op_group_name,
                "url": url_for('swagger.get_resource_in_rp',
                               plane=plane, mod_names=mod_names, rp_name=rp.name, resource_id=resource_id),
                "id": resource_id,
                "versions": []
            }
            for version, resource in version_map.items():
                rs['versions'].append({
                    "url": url_for('swagger.get_resource_version_in_rp',
                                   plane=plane, mod_names=mod_names, rp_name=rp.name,
                                   resource_id=resource.id, version=resource.version),
                    "version": version,
                    "file": resource.file_path,
                    "path": resource.path,
                    "operations": resource.operations
                })
            result['resources'].append(rs)
    return jsonify(result)


# resources
@bp.route("/<plane>/<list_path:mod_names>/ResourceProviders/<rp_name>/Resources", methods=("GET",))
def get_resources_by(plane, mod_names, rp_name):
    specs_manager = SwaggerSpecsManager()
    result = []
    rp = specs_manager.get_resource_provider(plane, mod_names, rp_name)
    resource_op_group_map = specs_manager.get_grouped_resource_map(plane, mod_names, rp_name)
    for op_group_name, resource_map in resource_op_group_map.items():
        for resource_id, version_map in resource_map.items():
            rs = {
                "opGroup": op_group_name,
                "url": url_for('swagger.get_resource_in_rp',
                               plane=plane, mod_names=mod_names, rp_name=rp.name, resource_id=resource_id),
                "id": resource_id,
                "versions": []
            }
            for version, resource in version_map.items():
                rs['versions'].append({
                    "url": url_for('swagger.get_resource_version_in_rp',
                                   plane=plane, mod_names=mod_names, rp_name=rp.name,
                                   resource_id=resource.id, version=resource.version),
                    "id": resource_id,
                    "version": version,
                    "file": resource.file_path,
                    "path": resource.path,
                    "operations": resource.operations
                })
            result.append(rs)
    return jsonify(result)


# resource
@bp.route("/<plane>/<list_path:mod_names>/ResourceProviders/<rp_name>/Resources/<base64:resource_id>",
          methods=("GET",))
def get_resource_in_rp(plane, mod_names, rp_name, resource_id):
    specs_manager = SwaggerSpecsManager()
    version_map = specs_manager.get_resource_version_map(
        plane=plane, mod_names=mod_names, resource_id=resource_id, rp_name=rp_name
    )
    rp = list(version_map.values())[0].resource_provider
    op_group_name = specs_manager.get_resource_op_group_name(version_map)
    result = {
        "opGroup": op_group_name,
        "url": url_for('swagger.get_resource_in_rp',
                       plane=plane, mod_names=mod_names, rp_name=rp.name, resource_id=resource_id),
        "id": resource_id,
        "versions": []
    }
    for version, resource in version_map.items():
        result['versions'].append({
            "url": url_for('swagger.get_resource_version_in_rp',
                           plane=plane, mod_names=mod_names, rp_name=rp.name,
                           resource_id=resource.id, version=resource.version),
            "id": resource_id,
            "version": version,
            "file": resource.file_path,
            "path": resource.path,
            "operations": resource.operations
        })
    return jsonify(result)


@bp.route("/<plane>/<list_path:mod_names>/Resources/<base64:resource_id>", methods=("GET",))
def get_resource_in_module(plane, mod_names, resource_id):
    specs_manager = SwaggerSpecsManager()
    version_map = specs_manager.get_resource_version_map(
        plane=plane, mod_names=mod_names, resource_id=resource_id
    )
    rp = list(version_map.values())[0].resource_provider
    op_group_name = specs_manager.get_resource_op_group_name(version_map)
    result = {
        "opGroup": op_group_name,
        "url": url_for('swagger.get_resource_in_rp',
                       plane=plane, mod_names=mod_names, rp_name=rp.name, resource_id=resource_id),
        "id": resource_id,
        "versions": []
    }
    for version, resource in version_map.items():
        result['versions'].append({
            "url": url_for('swagger.get_resource_version_in_rp',
                           plane=plane, mod_names=mod_names, rp_name=rp.name,
                           resource_id=resource.id, version=resource.version),
            "id": resource_id,
            "version": version,
            "file": resource.file_path,
            "path": resource.path,
            "operations": resource.operations
        })
    return jsonify(result)


# resource version
@bp.route(
    "/<plane>/<list_path:mod_names>/ResourceProviders/<rp_name>/Resources/<base64:resource_id>/V/<base64:version>",
    methods=("GET",)
)
def get_resource_version_in_rp(plane, mod_names, rp_name, resource_id, version):
    specs_manager = SwaggerSpecsManager()
    resource = specs_manager.get_resource_in_version(
        plane=plane, mod_names=mod_names, rp_name=rp_name, resource_id=resource_id, version=version
    )
    result = {
        "url": url_for('swagger.get_resource_version_in_rp',
                       plane=plane, mod_names=mod_names, rp_name=resource.resource_provider.name,
                       resource_id=resource.id, version=resource.version),
        "id": resource_id,
        "version": version,
        "file": resource.file_path,
        "path": resource.path,
        "operations": resource.operations
    }
    return jsonify(result)


@bp.route("/<plane>/<list_path:mod_names>/Resources/<base64:resource_id>/V/<base64:version>", methods=("GET",))
def get_resource_version_in_module(plane, mod_names, resource_id, version):
    specs_manager = SwaggerSpecsManager()
    resource = specs_manager.get_resource_in_version(
        plane=plane, mod_names=mod_names, resource_id=resource_id, version=version
    )
    result = {
        "url": url_for('swagger.get_resource_version_in_rp',
                       plane=plane, mod_names=mod_names, rp_name=resource.resource_provider.name,
                       resource_id=resource.id, version=resource.version),
        "id": resource_id,
        "version": version,
        "file": resource.file_path,
        "path": resource.path,
        "operations": resource.operations
    }
    return jsonify(result)
