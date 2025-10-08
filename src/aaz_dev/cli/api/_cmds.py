import click
import logging
from flask import Blueprint
import os
import sys

from cli.controller.az_module_manager import AzExtensionManager, AzMainManager
from command.controller.specs_manager import AAZSpecsManager
from command.controller.workspace_manager import WorkspaceManager
from command.model.configuration import CMDHelp
from swagger.controller.specs_manager import SwaggerSpecsManager
from swagger.model.specs import TypeSpecResourceProvider
from swagger.utils.source import SourceTypeEnum

from utils.config import Config
from utils.exceptions import InvalidAPIUsage

logger = logging.getLogger('aaz')

bp = Blueprint('cli-cmds', __name__, url_prefix='/CLI/CMDs', cli_group="cli")
bp.cli.short_help = "Manage aaz commands in azure-cli and azure-cli-extensions."


@bp.cli.command("regenerate", short_help="Regenerate aaz commands from command models in azure-cli/azure-cli-extensions")
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
    "--cli-path", '-c',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_path,
    help="The local path of azure-cli repo. Only required when generate code to azure-cli repo."
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_extension_path,
    help="The local path of azure-cli-extension repo. Only required when generate code to azure-cli-extension repo."
)
@click.option(
    "--extension-or-module-name", '--name',
    required=True,
    help="Name of the module in azure-cli or the extension in azure-cli-extensions"
)
def regenerate_code(extension_or_module_name, cli_path=None, cli_extension_path=None):
    if not cli_path and not cli_extension_path:
        logger.error("Please provide `--cli-path` or `--cli-extension-path`")
        sys.exit(1)
    if cli_path and cli_extension_path:
        logger.error("Please don't provide `--cli-path` and `--cli-extension-path`")
        sys.exit(1)

    try:
        if cli_path is not None:
            assert Config.CLI_PATH is not None
            manager = AzMainManager()
        else:
            assert cli_extension_path is not None
            assert Config.CLI_EXTENSION_PATH is not None
            manager = AzExtensionManager()

        if not manager.has_module(extension_or_module_name):
            # module = manager.create_new_mod(extension_or_module_name)
            raise ValueError(f"Cannot find module or extension `{extension_or_module_name}`")
        logger.info(f"Load module `{extension_or_module_name}`")
        module = manager.load_module(extension_or_module_name)
        logger.info(f"Regenerate module `{extension_or_module_name}`")
        manager.update_module(extension_or_module_name, module.profiles)
    except InvalidAPIUsage as err:
        logger.error(err)
        sys.exit(1)
    except ValueError as err:
        logger.error(err)
        sys.exit(1)


@bp.cli.command("generate-by-swagger-tag", short_help="Generate aaz commands from command models in azure-cli/azure-cli-extensions selected by swagger tags.")
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
    "--cli-path", '-c',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_path,
    help="The local path of azure-cli repo. Only required when generate code to azure-cli repo."
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_extension_path,
    help="The local path of azure-cli-extension repo. Only required when generate code to azure-cli-extension repo."
)
@click.option(
    "--extension-or-module-name", '--name',
    required=True,
    help="Name of the module in azure-cli or the extension in azure-cli-extensions"
)
@click.option(
    "--swagger-module-path", "--sm",
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_MODULE_PATH,
    required=not Config.SWAGGER_MODULE_PATH,
    callback=Config.validate_and_setup_swagger_module_path,
    expose_value=False,
    help="The local path of swagger module."
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
    "--profile",
    required=True,
    type=click.Choice(Config.CLI_PROFILES),
    default=Config.CLI_DEFAULT_PROFILE,
)
def generate_by_swagger_tag(profile, swagger_tag, extension_or_module_name, cli_path=None, cli_extension_path=None):
    if not Config.DEFAULT_SWAGGER_MODULE:
        Config.DEFAULT_SWAGGER_MODULE = "__MODULE__"

    try:
        swagger_specs = SwaggerSpecsManager()
        aaz_specs = AAZSpecsManager()
        module_manager = swagger_specs.get_module_manager(Config.DEFAULT_PLANE, Config.DEFAULT_SWAGGER_MODULE)
        rp = module_manager.get_openapi_resource_provider(Config.DEFAULT_RESOURCE_PROVIDER)

        resource_map = rp.get_resource_map_by_tag(swagger_tag)
        if not resource_map:
            raise InvalidAPIUsage(f"Tag `{swagger_tag}` is not exist")

        commands_map = {}
        for resource_id, version_map in resource_map.items():
            v_list = [v for v in version_map]
            if len(v_list) > 1:
                raise InvalidAPIUsage(f"Tag `{swagger_tag}` contains multiple api versions of one resource", payload={
                    "Resource": resource_id,
                    "versions": v_list,
                })

            v = v_list[0]
            # TODO: handle plane here
            cfg_reader = aaz_specs.load_resource_cfg_reader(Config.DEFAULT_PLANE, resource_id, v)
            if not cfg_reader:
                logger.error(f"Command models not exist in aaz for resource: {resource_id} version: {v}")
                continue
            for cmd_names, command in cfg_reader.iter_commands():
                key = tuple(cmd_names)
                if key in commands_map and commands_map[key] != command.version:
                    raise ValueError(f"Multi version contained for command: {''.join(cmd_names)} versions: {commands_map[key]}, {command.version}")
                commands_map[key] = command.version

        profile = _build_profile(profile, commands_map)

        if cli_path is not None:
            assert Config.CLI_PATH is not None
            manager = AzMainManager()
        else:
            assert cli_extension_path is not None
            assert Config.CLI_EXTENSION_PATH is not None
            manager = AzExtensionManager()

        if not manager.has_module(extension_or_module_name):
            logger.info(f"Create cli module `{extension_or_module_name}`")
            manager.create_new_mod(extension_or_module_name)

        logger.info(f"Load cli module `{extension_or_module_name}`")
        module = manager.load_module(extension_or_module_name)

        module.profiles[profile.name] = profile
        logger.info(f"Regenerate module `{extension_or_module_name}`")
        manager.update_module(extension_or_module_name, module.profiles)

    except InvalidAPIUsage as err:
        logger.error(err)
        sys.exit(1)
    except ValueError as err:
        logger.error(err)
        sys.exit(1)


@bp.cli.command("generate", short_help="Generate code effortlessly. If the result isn't what you expected, use the UI to fine-tune it.")
@click.option(
    "--cli-path", "-c",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.CLI_PATH,
    callback=Config.validate_and_setup_cli_path,
    expose_value=False,
    help="Local path of azure-cli repo. Only required when generate code to azure-cli repo."
)
@click.option(
    "--spec", "-s",
    required=True,
    help="Folder name of the specification source."
)
@click.option(
    "--module", "-m",
    required=True,
    help="Module name of the CLI extension target."
)
def generate(spec, module, cli_path=None):
    def _collect_resources(spec):
        module_manager = SwaggerSpecsManager().get_module_manager(Config.DEFAULT_PLANE, spec)
        rps = module_manager.get_resource_providers()

        results = {}
        for r in rps:
            if isinstance(r, TypeSpecResourceProvider):
                continue

            rp = module_manager.get_openapi_resource_provider(r.name)
            tag = r.default_tag

            resource_map = rp.get_resource_map_by_tag(tag)
            if not resource_map:
                raise InvalidAPIUsage(f"Tag `{tag}` is not exist.")

            results[rp.name] = (resource_map, tag)

        return results

    def _normalize_resource_map(resource_map, tag):
        # covert resource_map to {version: [resources]}
        version_resource_map = {}
        for resource_id, version_map in resource_map.items():
            v_list = list(version_map)
            if len(v_list) > 1:
                raise InvalidAPIUsage(
                    f"Tag `{tag}` contains multiple api versions of one resource",
                    payload={"Resource": resource_id, "versions": v_list},
                )

            v = v_list[0]
            version_resource_map.setdefault(v, []).append({"id": resource_id})

        return version_resource_map

    def to_aaz():
        results = _collect_resources(spec)

        for rp_name, (resource_map, tag) in results.items():
            version_resource_map = _normalize_resource_map(resource_map, tag)

            ws = WorkspaceManager.new(
                name=spec,
                plane=Config.DEFAULT_PLANE,
                folder=WorkspaceManager.IN_MEMORY,
                mod_names=spec,
                resource_provider=rp_name,
                swagger_manager=SwaggerSpecsManager(),
                aaz_manager=AAZSpecsManager(),
                source=SourceTypeEnum.OpenAPI,
            )
            for version, resources in version_resource_map.items():
                ws.add_new_resources_by_swagger(mod_names=spec, version=version, resources=resources)

            # complete default help
            for node in ws.iter_command_tree_nodes():
                node.help = node.help or CMDHelp()
                if not node.help.short:
                    node.help.short = f"Manage {node.names[-1]}."

            for leaf in ws.iter_command_tree_leaves():
                leaf.help = leaf.help or CMDHelp()
                if not leaf.help.short:
                    n = leaf.names[-1]
                    leaf.help.short = f"{n.capitalize()} {leaf.names[-2]}"

                cfg_editor = ws.load_cfg_editor_by_command(leaf)
                command = cfg_editor.find_command(*leaf.names)
                leaf.examples = ws.generate_examples_by_swagger(leaf, command)

            if not ws.is_in_memory:
                ws.save()

            ws.generate_to_aaz()

    def to_cli():
        results = _collect_resources(spec)

        commands_map = {}
        for _, (resource_map, tag) in results.items():
            for resource_id, version_map in resource_map.items():
                v_list = list(version_map)
                if len(v_list) > 1:
                    raise InvalidAPIUsage(
                        f"Tag `{tag}` contains multiple api versions of one resource",
                        payload={"Resource": resource_id, "versions": v_list},
                    )

                v = v_list[0]
                cfg_reader = AAZSpecsManager().load_resource_cfg_reader(Config.DEFAULT_PLANE, resource_id, v)
                if not cfg_reader:
                    logger.error(f"Command models not exist in aaz for resource: {resource_id} version: {v}.")
                    continue

                for cmd_names, command in cfg_reader.iter_commands():
                    key = tuple(cmd_names)
                    if key in commands_map and commands_map[key] != command.version:
                        raise ValueError(f"Multi version contained for command: {''.join(cmd_names)} versions: {commands_map[key]}, {command.version}")

                    commands_map[key] = command.version

        if cli_path is not None:
            assert Config.CLI_PATH is not None
            manager = AzMainManager()

        else:  # generate ext module by default
            assert Config.CLI_EXTENSION_PATH is not None
            manager = AzExtensionManager()

        if not manager.has_module(module):
            logger.info(f"Create cli module `{module}`.")
            manager.create_new_mod(module)

        logger.info(f"Load cli module `{module}`.")
        ext = manager.load_module(module)

        profile = _build_profile(Config.CLI_DEFAULT_PROFILE, commands_map)
        ext.profiles[profile.name] = profile

        logger.info(f"Regenerate module `{module}`.")
        manager.update_module(module, ext.profiles)

    spec_path = os.path.join(Config.SWAGGER_PATH, "specification", spec)
    if not os.path.exists(spec_path) or not os.path.isdir(spec_path):
        raise ValueError(f"Cannot find the specification name under {Config.SWAGGER_PATH}.")

    try:
        to_aaz()
        logger.info("✅ Finished generating AAZ model.")
        to_cli()
        logger.info("✅ Finished generating AAZ codes.")

    except (InvalidAPIUsage, ValueError) as err:
        logger.error(err, exc_info=True)
        raise sys.exit(1)


def _build_profile(profile_name, commands_map):
    from cli.model.view import CLIViewProfile, CLIViewCommand, CLIViewCommandGroup
    profile = CLIViewProfile({
        "name": profile_name,
        "commandGroups": {},
    })
    command_group_map = {tuple(): profile}
    for cmd_names, version in commands_map.items():
        group_names = cmd_names[:-1]
        if group_names not in command_group_map:
            group = CLIViewCommandGroup({
                "names": list(group_names),
                "commandGroups": {},
                "commands": {}
            })
        else:
            group = command_group_map[group_names]
        group.commands[cmd_names[-1]] = CLIViewCommand({
            "names": list(cmd_names),
            "version": version,
            "registered": True
        })

        while group_names not in command_group_map:
            command_group_map[group_names] = group
            parent_group_names = group_names[:-1]
            if parent_group_names not in command_group_map:
                parent_group = CLIViewCommandGroup({
                    "names": list(parent_group_names),
                    "commandGroups": {},
                    "commands": {}
                })
            else:
                parent_group = command_group_map[parent_group_names]
            parent_group.command_groups[group_names[-1]] = group

            group = parent_group
            group_names = parent_group_names

    return profile
