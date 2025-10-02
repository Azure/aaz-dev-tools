import click
import json
import logging
import os
import re
import sys
from collections import defaultdict
from flask import Blueprint

from command.controller.specs_manager import AAZSpecsManager
from command.controller.workspace_manager import WorkspaceManager
from command.model.configuration import CMDHelp
from swagger.controller.specs_manager import SwaggerSpecsManager
from swagger.model.specs import TypeSpecResourceProvider
from swagger.utils.source import SourceTypeEnum
from swagger.utils.tools import swagger_resource_path_to_resource_id

from utils.config import Config
from utils.exceptions import InvalidAPIUsage

logger = logging.getLogger('aaz')

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
    try:
        swagger_specs = SwaggerSpecsManager()
        aaz_specs = AAZSpecsManager()

        module_manager = swagger_specs.get_module_manager(Config.DEFAULT_PLANE, Config.DEFAULT_SWAGGER_MODULE)
        rp = module_manager.get_openapi_resource_provider(Config.DEFAULT_RESOURCE_PROVIDER)

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

        mod_names = Config.DEFAULT_SWAGGER_MODULE
        ws = WorkspaceManager.new(
            name=Config.DEFAULT_SWAGGER_MODULE,
            plane=Config.DEFAULT_PLANE,
            folder=workspace_path or WorkspaceManager.IN_MEMORY,  # if workspace path exist, use workspace else use in memory folder
            mod_names=mod_names,
            resource_provider=rp.name,
            swagger_manager=swagger_specs,
            aaz_manager=aaz_specs,
            source=SourceTypeEnum.OpenAPI,
        )
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
            # generate examples
            cfg_editor = ws.load_cfg_editor_by_command(leaf)
            command = cfg_editor.find_command(*leaf.names)
            examples = ws.generate_examples_by_swagger(leaf, command)
            leaf.examples = examples

        if not ws.is_in_memory:
            ws.save()

        ws.generate_to_aaz()

    except InvalidAPIUsage as err:
        logger.error(err)
        sys.exit(1)
    except ValueError as err:
        logger.error(err)
        sys.exit(1)


@bp.cli.command("generate-all", short_help="Fully generate data model from OpenAPI specification, mainly for use in https://github.com/magodo/az-rs.")
@click.option(
    "--swagger-path", '-s',
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_PATH,
    callback=Config.validate_and_setup_swagger_path,
    expose_value=False,
    help="The local path of azure-rest-api-specs repo. Official repo is https://github.com/Azure/azure-rest-api-specs"
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
    callback=Config.validate_and_setup_default_swagger_module,
    expose_value=False,
    help="The name of swagger module."
)
def generate_all():
    def update_strategy(resource):
        has_patch = "patch" in resource.operations.values()
        # has_generic_update = {"get", "put"}.issubset(resource.operations.values())
        if has_patch:
            return "PatchOnly"
        # if has_generic_update:  # fallback to get + put
        #     return "None"
        return None

    def normalize_resource_map(resource_map):
        version_resource_map = defaultdict(list)
        for resource_id, version_map in resource_map.items():
            for version in sorted(version_map.keys())[-4:]:  # only care about the latest 4 versions
                resource = {"id": resource_id}
                update_by = update_strategy(version_map[version])
                if update_by:
                    resource["options"] = {"update_by": update_by}

                version_resource_map[version].append(resource)

        return version_resource_map

    def to_aaz(module_name):
        module_manager = SwaggerSpecsManager().get_module_manager(Config.DEFAULT_PLANE, module_name)
        rps = module_manager.get_resource_providers()

        for r in rps:
            if isinstance(r, TypeSpecResourceProvider):
                continue

            rp = module_manager.get_openapi_resource_provider(r.name)
            version_resource_map = normalize_resource_map(rp.get_resource_map())

            for version, resources in version_resource_map.items():
                ws = WorkspaceManager.new(
                    name=module_name,
                    plane=Config.DEFAULT_PLANE,
                    folder=WorkspaceManager.IN_MEMORY,
                    mod_names=module_name,
                    resource_provider=rp.name,
                    swagger_manager=SwaggerSpecsManager(),
                    aaz_manager=AAZSpecsManager(),
                    source=SourceTypeEnum.OpenAPI,
                )
                ws.add_new_resources_by_swagger(mod_names=module_name, version=version, resources=resources)

                # provide default short summary
                for node in ws.iter_command_tree_nodes():
                    if not node.help:
                        node.help = CMDHelp()
                    if not node.help.short:
                        node.help.short = f"Manage {node.names[-1]}."

                for leaf in ws.iter_command_tree_leaves():
                    if not leaf.help:
                        leaf.help = CMDHelp()
                    if not leaf.help.short:
                        n = leaf.names[-1]
                        n = n[0].upper() + n[1:]
                        leaf.help.short = f"{n} {leaf.names[-2]}."

                ws.generate_to_aaz()

    try:
        if Config.DEFAULT_SWAGGER_MODULE:
            to_aaz(Config.DEFAULT_SWAGGER_MODULE)

        else:
            spec_path = os.path.join(Config.SWAGGER_PATH, "specification")
            for item in os.listdir(spec_path):
                curr_path = os.path.join(spec_path, item)
                if os.path.isfile(curr_path):
                    continue

                to_aaz(item)

    except (InvalidAPIUsage, ValueError) as err:
        logger.error(err, exc_info=True)
        raise sys.exit(1)


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
@click.option(
    "--target", "-t",
    help="Target module to focus on."
)
def verify(target):
    def verify_resource(model, path):
        if "commandGroups" not in model:
            return

        for grp in model["commandGroups"]:
            base_path = os.path.join(path, *grp["name"].split())
            if not os.path.exists(base_path):
                raise FileNotFoundError(base_path)

            for cmd in grp.get("commands", []):
                file_path = os.path.join(base_path, f"_{cmd['name']}.md")
                if not os.path.isfile(file_path):
                    raise FileNotFoundError(file_path)

            verify_resource(grp, base_path)

    def verify_command(file_path):
        with open(file_path, "r", encoding="utf-8") as fp:
            content = fp.read()

        base_path = os.path.dirname(file_path)
        curr_grp = " ".join(os.path.relpath(base_path, aaz.commands_folder).split(os.sep))
        curr_cmd = os.path.splitext(os.path.basename(file_path))[0][1:]

        paths = re.findall(r"]\(([^)]+)\)", content)
        for path in paths:
            json_path = os.path.join(Config.AAZ_PATH, os.path.splitext(path)[0][1:] + ".json")
            json_path = os.path.normpath(json_path)

            if not os.path.exists(json_path):
                raise Exception(f"{json_path} defined in {file_path} is missing.")

            with open(json_path, "r", encoding="utf-8", errors="ignore") as fp:
                model = json.load(fp)

            try:
                verify_resource(model, aaz.commands_folder)

            except FileNotFoundError as e:
                raise Exception(f"Cannot find {e} defined in {json_path}.")

            target = curr_grp
            while target:
                try:
                    for grp in model["commandGroups"]:
                        if target.startswith(grp["name"]):
                            target = target[len(grp["name"]):].strip()
                            model = grp

                            break

                except KeyError:
                    raise Exception(f"{curr_grp} has no corresponding definition in {json_path}.")

            commands = model["commands"]
            if not any(cmd["name"] == curr_cmd for cmd in commands):
                raise Exception(f"There is no {curr_cmd} command info in {json_path}.")

            model_set.add(json_path)

    model_set = set()
    aaz = AAZSpecsManager()

    parent = aaz.commands_folder
    stack = [os.path.join(parent, target)] if target else [
        os.path.join(parent, i)
        for i in os.listdir(parent)
        if os.path.isdir(os.path.join(parent, i))
    ]

    while stack:
        curr_path = stack.pop()
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

                    for file in files:
                        verify_command(os.path.join(curr_path, file))

                else:
                    if len(items) != len(set(items)):
                        raise Exception(f"{readme_path} has duplicate command group names.")

                    items = set(items)

                    folders = {i for i in os.listdir(curr_path) if os.path.isdir(os.path.join(curr_path, i))}
                    if folders != items:
                        diff = folders - items or items - folders
                        raise Exception(f"Command group info {diff} doesn't match in {readme_path}.")

                    for folder in folders:
                        stack.append(os.path.join(curr_path, folder))

    if not target:
        for root, _, files in os.walk(aaz.resources_folder):
            for file in files:
                if not file.endswith(".json") or file.startswith("client"):  # support data-plane
                    continue

                file_path = os.path.join(root, file)
                if file_path not in model_set:
                    raise Exception(f"{file_path} is redundant.")


@bp.cli.command("transform", short_help="Transform into machine-friendly metadata.")
@click.option(
    "--aaz-path", "-a",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="Path of `aaz` repository."
)
def transform():
    def nested_dict():
        return defaultdict(nested_dict)

    def process_resource(model):
        resources = []
        for resource in model["resources"]:
            resources.append({
                "id": resource["id"],
                "plane": model["plane"]
            })

        return resources

    def export_command(xml_path, file_name):
        json_path = os.path.normpath(os.path.join(Config.AAZ_PATH, f"{os.path.splitext(xml_path)[0][1:]}.json"))
        with open(json_path, "r", encoding="utf-8", errors="ignore") as f:
            model = json.load(f)

        target = file_name.split("_")[-2]  # command name

        data = {"resources": process_resource(model)}
        for cmd in model["commandGroups"][0].get("commands", []):
            if cmd["name"] == target:
                other = {k: v for k, v in cmd.items() if k not in {"name", "version", "resources"}}
                data = {**data, **other}

                break

        with open(os.path.join("./metadata/commands", file_name), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    def build_command(path):
        command = defaultdict(nested_dict)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        command["help"]["short"] = re.findall(r"# \[Command\].*?\n\n(.*?)\n", content)[0]
        command["versions"] = []

        matches = re.findall(r"### \[(.*?)\]\((.*?)\)", content)
        for version, xml_path in matches:
            command["versions"].insert(0, version)

            *grp, cmd_md = os.path.relpath(path, aaz_commands).split(os.sep)
            export_command(xml_path, f"{'_'.join(grp)}_{cmd_md[1:-3]}_{version}.json")

        return command

    def build_group(path):
        group = defaultdict(nested_dict)
        for item in sorted(os.listdir(path)):
            curr_path = os.path.join(path, item)
            if item == "readme.md":
                with open(curr_path, "r", encoding="utf-8") as f:
                    content = f.read()

                group["help"]["short"] = re.findall(r"# \[Group\].*?\n\n(.*?)\n", content)[0]
                continue

            if os.path.isdir(curr_path):
                group["commandGroups"][item] = build_group(curr_path)

            else:
                group["commands"][item[1:-3]] = build_command(curr_path)

        return group

    os.makedirs("metadata/commands")
    index = defaultdict(nested_dict)

    aaz_commands = AAZSpecsManager().commands_folder
    for item in sorted(os.listdir(aaz_commands)):
        curr_path = os.path.join(aaz_commands, item)
        if os.path.isdir(curr_path):
            index[item] = build_group(curr_path)

    with open(os.path.join("./metadata", "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
