import click
import logging
from flask import Blueprint
import sys

from swagger.utils.tools import swagger_resource_path_to_resource_id
from utils.config import Config

logger = logging.getLogger('backend')

bp = Blueprint('aaz-cmds', __name__, url_prefix='/AAZ/CMDs', cli_group="command-model")
bp.cli.short_help = "Manage command models in aaz."


def path_type(ctx, param, value):
    import os
    return os.path.expanduser(value)


def resource_id_type(value):
    return swagger_resource_path_to_resource_id(value)


@bp.cli.command("generate-from-swagger", short_help="Generate command models into aaz from swagger specs")
@click.option(
    "--swagger-path", '-s',
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_PATH,
    callback=Config.validate_and_setup_swagger_path,
    expose_value=False,
    help="The local path of azure-rest-api-specs repo. Official repo is https://github.com/Azure/azure-rest-api-specs"
)
@click.option(
    "--swagger-module-path", "--sm",
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_MODULE_PATH,
    callback=Config.validate_and_setup_swagger_module_path,
    expose_value=False,
    help="The local path of swagger in module level. It can be substituted for --swagger-path."
)
@click.option(
    "--aaz-path", '-a',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="The local path of aaz repo."
)
@click.option(
    "--module", '-m',
    default=Config.DEFAULT_SWAGGER_MODULE,
    required=not Config.DEFAULT_SWAGGER_MODULE,
    callback=Config.validate_and_setup_default_swagger_module,
    expose_value=False,
    help="The name of swagger module."
)
@click.option(
    "--resource-provider", "--rp",
    default=Config.DEFAULT_RESOURCE_PROVIDER,
    required=not Config.DEFAULT_RESOURCE_PROVIDER,
    callback=Config.validate_and_setup_default_resource_provider,
    expose_value=False,
    help="The resource provider name."
)
@click.option(
    "--swagger-tag", "--tag",
    required=True,
    help="Swagger tag with input files."
)
@click.option(
    "--workspace-path",
    help="The path to export the workspace for modification."
)
def generate_command_models_from_swagger(swagger_tag, workspace_path=None):
    from swagger.controller.specs_manager import SwaggerSpecsManager
    from command.controller.specs_manager import AAZSpecsManager
    from command.controller.workspace_manager import WorkspaceManager
    from utils.config import Config
    from utils.exceptions import InvalidAPIUsage
    from command.model.configuration import CMDHelp

    try:
        swagger_specs = SwaggerSpecsManager()
        aaz_specs = AAZSpecsManager()

        module_manager = swagger_specs.get_module_manager(Config.DEFAULT_PLANE, Config.DEFAULT_SWAGGER_MODULE)
        rp = module_manager.get_resource_provider(Config.DEFAULT_RESOURCE_PROVIDER)

        resource_map = rp.get_resource_map_by_tag(swagger_tag)
        if not resource_map:
            raise InvalidAPIUsage(f"Tag `{swagger_tag}` is not exist")

        version_resource_map = {}
        for resource_id, version_map in resource_map.items():
            v_list = [v for v in version_map]
            if len(v_list) > 1:
                raise InvalidAPIUsage(f"Tag `{swagger_tag}` contains multiple api versions of one resource", payload={
                    "Resource": resource_id,
                    "versions": v_list,
                })
            v = v_list[0]
            if v not in version_resource_map:
                version_resource_map[v] = []
            version_resource_map[v].append({
                "id": resource_id
            })

        ws = WorkspaceManager.new(
            name=Config.DEFAULT_SWAGGER_MODULE,
            plane=Config.DEFAULT_PLANE,
            folder=workspace_path or WorkspaceManager.IN_MEMORY,  # if workspace path exist, use workspace else use in memory folder
            swagger_manager=swagger_specs,
            aaz_manager=aaz_specs,
        )
        mod_names = Config.DEFAULT_SWAGGER_MODULE.split('/')
        for version, resources in version_resource_map.items():
            ws.add_new_resources_by_swagger(
                mod_names=mod_names, version=version, resources=resources
            )

        # provide default short summary
        for node in ws.iter_command_tree_nodes():
            if not node.help:
                node.help = CMDHelp()
            if not node.help.short:
                node.help.short = f"Manage {node.names[-1]}"

        for leaf in ws.iter_command_tree_leaves():
            if not leaf.help:
                leaf.help = CMDHelp()
            if not leaf.help.short:
                n = leaf.names[-1]
                n = n[0].upper() + n[1:]
                leaf.help.short = f"{n} {leaf.names[-2]}"

        if not ws.is_in_memory:
            ws.save()

        ws.generate_to_aaz()

    except InvalidAPIUsage as err:
        logger.error(err)
        sys.exit(1)
    except ValueError as err:
        logger.error(err)
        sys.exit(1)
