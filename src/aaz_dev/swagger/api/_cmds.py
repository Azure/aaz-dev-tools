import click
import logging
from flask import Blueprint
import os
import json

from utils.config import Config

logger = logging.getLogger('backend')

bp = Blueprint('swagger-cmds', __name__, url_prefix='/Swagger/CMDs', cli_group="swagger")
bp.cli.short_help = "Manage azure-rest-api-specs/azure-rest-api-specs-pr repos."

@bp.cli.command("export-resources", short_help="Export all control plane resources in swagger repo")
@click.option(
    "--swagger-path", '-s',
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_PATH,
    required=not Config.SWAGGER_PATH,
    callback=Config.validate_and_setup_swagger_path,
    expose_value=False,
    help="The local path of azure-rest-api-specs repo. Official repo is https://github.com/Azure/azure-rest-api-specs"
)
@click.option(
    "--output-file", '-o',
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True),
    help="The file name for result output",
)
def export_swagger_control_plane_resources(output_file):
    logger.setLevel(level=logging.CRITICAL)
    from swagger.controller.specs_manager import SwaggerSpecsManager
    from utils.plane import PlaneEnum

    if output_file and os.path.exists(output_file):
        print(f"The output file {output_file} exists. Do you want to override it? (Y/N):", end='')
        if input().lower() != 'y':
            print("Exit without overriding.")
            return

    result = {}
    swagger_specs = SwaggerSpecsManager()
    for module in swagger_specs.get_modules(PlaneEnum.Mgmt):
        for rp in module.get_resource_providers():
            if rp.name.lower() not in result:
                result[rp.name.lower()] = {}
            resource_map = result[rp.name.lower()]
            for resource_id, version_map in rp.get_resource_map().items():
                if resource_id not in resource_map:
                    resource_map[resource_id] = set()
                resource_map[resource_id].update([version for version in version_map])
    for rp, resource_map in result.items():
        for resource in resource_map:
            assert None not in resource_map[resource]
            resource_map[resource] = sorted(resource_map[resource])

    if output_file is None:
        print(json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2))
    else:
        with open(output_file, 'w') as f:
            json.dump(result, f, ensure_ascii=True, sort_keys=True, indent=2)
        print(f'Export output in {output_file} success.')
