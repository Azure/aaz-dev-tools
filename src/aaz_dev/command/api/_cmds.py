import click
import json
import logging
import os
import re
import sys
from flask import Blueprint

from command.controller.specs_manager import AAZSpecsManager
from command.templates import get_templates
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


@bp.cli.command("verify", short_help="Verify data consistency within `aaz` repository.")
@click.option(
    "--aaz-path", "-a",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="Path of `aaz` repository."
)
def verify():
    def verify_command(file_path, node):
        with open(file_path, "r", encoding="utf-8") as fp:
            content = fp.read()

        paths = re.findall(r"]\(([^)]+)\)", content)
        for path in paths:
            json_path = os.path.join(Config.AAZ_PATH, os.path.splitext(path)[0][1:] + ".json")
            json_path = os.path.normpath(json_path)
            if not os.path.exists(json_path):
                raise Exception(f"{json_path} defined in {file_path} is missing.")

            with open(json_path, "r", encoding="utf-8", errors="ignore") as fp:
                model = json.load(fp)
            group, command = " ".join(node.names[:-1]), node.names[-1]
            for g in model["commandGroups"]:
                if g["name"] == group:
                    if not any(cmd["name"] == command for cmd in g["commands"]):
                        raise Exception(f"There is no {command} command info in {json_path}.")

                    break

            model_set.add(json_path)

        tmpl = get_templates()["command"]
        if not tmpl.render(command=node) == content:
            raise Exception(f"{file_path} cannot be rendered correctly.")

    model_set = set()
    aaz = AAZSpecsManager()
    stack = [(aaz.commands_folder, aaz.tree.root)]  # root nodes

    while stack:
        curr_path, curr_node = stack.pop()
        logger.info(f"Checking {curr_path}")
        if os.path.isdir(curr_path):
            readme_path = os.path.join(curr_path, "readme.md")
            if not os.path.exists(readme_path):
                raise Exception(f"Missing `readme.md` under {curr_path}.")

            with open(readme_path, "r", encoding="utf-8") as fp:
                content = fp.read()

            matches = re.findall(r"## (.+)\n\n(((?!\n##)[\s\S])+)", content)
            for match in matches:
                level = match[0]
                items = re.findall(r"- \[([^[\]]+)]", match[1])

                if level == "Commands":
                    if len(items) != len(set(items)):
                        raise Exception(f"{readme_path} has duplicate command names.")

                    items = set(items)

                    files = {i for i in os.listdir(curr_path) if os.path.isfile(os.path.join(curr_path, i))}
                    files.remove("readme.md")

                    if (cmd_set := set(map(lambda x: x[1:-3], files))) != items:  # _<command_name>.md
                        diff = cmd_set - items or items - cmd_set
                        raise Exception(f"Command info {diff} doesn't match in {readme_path}.")

                    groups = set(curr_node.commands.keys())
                    if groups != items:
                        diff = groups - items or items - groups
                        raise Exception(f"Command info {diff} in tree.json doesn't match in {readme_path}.")

                    for file in files:
                        verify_command(os.path.join(curr_path, file), curr_node.commands[file[1:-3]])
                else:
                    if len(items) != len(set(items)):
                        raise Exception(f"{readme_path} has duplicate command group names.")

                    items = set(items)

                    folders = {i for i in os.listdir(curr_path) if os.path.isdir(os.path.join(curr_path, i))}
                    if folders != items:
                        diff = folders - items or items - folders
                        raise Exception(f"Command group info {diff} doesn't match in {readme_path}.")

                    groups = set(curr_node.command_groups.keys())
                    if groups != set(items):
                        diff = groups - items or items - groups
                        raise Exception(f"Command group info {diff} in tree.json doesn't match in {readme_path}.")

                    for folder in folders:
                        stack.append((os.path.join(curr_path, folder), curr_node.command_groups[folder]))

    for root, dirs, files in os.walk(aaz.resources_folder):
        for file in files:
            if not file.endswith(".json"):
                continue

            file_path = os.path.join(root, file)
            if file_path not in model_set:
                raise Exception(f"{file_path} is redundant.")
