import click
import logging
from flask import Blueprint
import os
import json
import zlib

from protos import component_pb2, command_pb2, argument_pb2
from protos.plugin import (
    model_pb2,
    resource_pb2,
    operation_pb2,
    output_pb2,
    selector_pb2,
    condition_pb2,
    http_pb2,
    schema_pb2,
)
from google.protobuf.json_format import MessageToJson
from command.controller.specs_manager import AAZSpecsManager
from utils.config import Config

logger = logging.getLogger("backend")

bp = Blueprint("cirrus-cmds", __name__, url_prefix="/CIRRUS/CMDs", cli_group="cirrus")
bp.cli.short_help = "Generate aaz models as cirrus components."


@bp.cli.command(
    "export-component", short_help="Export aaz models as a cirrus component."
)
@click.option(
    "--aaz-path",
    "-a",
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True
    ),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="The local path of aaz repo.",
)
@click.option(
    "--output-path",
    "-o",
    required=True,
    help="The output path where the component will be exported.",
)
@click.option("--component-name", "--name", required=True, help="Name of the component")
def export_component(component_name, output_path):
    print(f"Using AAZ path: {Config.AAZ_PATH}")
    module_name = component_name.lower()
    print(f"Exporting component: {module_name}")
    proto_component = create_component_proto(module_name)
    save_component_proto(proto_component, output_path, module_name, if_debug=True)


class OutdatedVersionTracker:
    """
    Singleton class to track and record commands that are not using the latest resource version.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OutdatedVersionTracker, cls).__new__(cls)
            cls._instance.outdated_commands = {}
        return cls._instance

    def record_outdated_command(
        self, command_name, command_version, latest_version, resource_id
    ):
        self.outdated_commands[command_name] = {
            "command_name": command_name,
            "command_version": command_version,
            "latest_version": latest_version,
            "resource_id": resource_id,
        }

    def save_to_file(self, output_path=None):
        if not self.outdated_commands:
            print("All commands are using their latest resource versions.")
            return

        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "not_using_latest_version.json",
            )

        print("\nOutdated Commands Summary:")
        print("=" * 80)
        for cmd_name, cmd_info in self.outdated_commands.items():
            print(f"Command: {cmd_name}")
            print(f"  Current Version: {cmd_info['command_version']}")
            print(f"  Latest Version: {cmd_info['latest_version']}")
            print(f"  Resource ID: {cmd_info['resource_id']}")
            print("-" * 80)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.outdated_commands, f, indent=2, ensure_ascii=False)

        print(
            f"\nRecorded {len(self.outdated_commands)} commands not using latest versions to {output_path}"
        )


outdated_version_tracker = OutdatedVersionTracker()
command_num = 0


@bp.cli.command(
    "export-all-modules",
    short_help="Export all AAZ modules and their command configurations.",
)
@click.option(
    "--aaz-path",
    "-a",
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True
    ),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="The local path of aaz repo.",
)
@click.option(
    "--output-path",
    "-o",
    required=True,
    help="The output path where the command configurations will be exported.",
)
def export_all_modules(output_path):
    print(f"Using AAZ path: {Config.AAZ_PATH}")

    specs_manager = AAZSpecsManager()

    os.makedirs(output_path, exist_ok=True)

    root_module = specs_manager.tree.root
    if not root_module:
        print("Root module not found!")
        return
    for module_name, module in root_module.command_groups.items():
        command_group = specs_manager.find_command_group(module_name)
        if command_group:
            print(f"Found module: {module_name}")
            proto_component = create_component_proto(module_name)
            save_component_proto(
                proto_component, output_path, module_name, if_debug=True
            )

    outdated_version_tracker.save_to_file()
    print(f"\nExported {command_num} commands")
    print(f"\nExported command configurations to {output_path}")


def save_component_proto(proto_component, output_path, module_name, if_debug=False):
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(os.path.join(output_path, "binary"), exist_ok=True)
    binary_file = os.path.join(output_path, "binary", f"{module_name}.pb")
    serialized_data = proto_component.SerializeToString()
    with open(binary_file, "wb") as f:
        f.write(serialized_data)
    print(f"Component protobuf saved to: {binary_file}")

    compressed_data = zlib.compress(serialized_data)
    os.makedirs(os.path.join(output_path, "binary_zipped"), exist_ok=True)
    binary_zipped_file = os.path.join(
        output_path, "binary_zipped", f"{module_name}.plugin"
    )
    with open(binary_zipped_file, "wb") as f:
        f.write(compressed_data)
    print(f"Component protobuf (zipped) saved to: {binary_zipped_file}")

    if if_debug:
        os.makedirs(os.path.join(output_path, "json"), exist_ok=True)
        json_file = os.path.join(output_path, "json", f"{module_name}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json_data = MessageToJson(
                proto_component,
                preserving_proto_field_name=True,
                sort_keys=True,
                indent=2,
            )
            f.write(json_data)
        print(f"Component JSON saved to: {json_file}")


def create_component_proto(module_name):
    specs_manager = AAZSpecsManager()
    root_module = specs_manager.find_command_group(module_name)
    component_version = "0.0.1"  # Hardcoded for now, can be replaced with dynamic versioning logic if needed
    proto_component = component_pb2.CrsPluginComponent()
    proto_component.metadata.name = module_name
    component_uri = f"crs://azure/{module_name}/"
    proto_component.metadata.version = component_version
    proto_component.metadata.uri = component_uri
    if root_module.help:
        proto_component.metadata.help.CopyFrom(
            convert_aaz_help_to_proto(root_module.help)
        )

    resource_latest_versions_map_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "latest_versions_by_resource_id.json",
    )
    try:
        with open(
            resource_latest_versions_map_file_path, "r", encoding="utf-8"
        ) as file:
            resource_latest_versions_map = json.load(file)
        print(
            f"Loaded latest versions map from: {resource_latest_versions_map_file_path}"
        )
    except FileNotFoundError:
        logging.warning(
            f"Warning: latest_versions_by_resource_id.json not found at {resource_latest_versions_map_file_path}"
        )
        resource_latest_versions_map = {}
    except json.JSONDecodeError:
        logging.warning(
            f"Warning: latest_versions_by_resource_id.json contains invalid JSON"
        )
        resource_latest_versions_map = {}

    print(
        f"\nFiltering commands to include only those using the latest resource API versions..."
    )
    proto_group = convert_aaz_command_group_to_proto(
        root_module, resource_latest_versions_map
    )
    proto_component.interface.command_group.CopyFrom(proto_group)

    return proto_component


def convert_aaz_help_to_proto(aaz_help):
    proto_help = command_pb2.CrsHelp()
    if aaz_help.get("short"):
        proto_help.short = aaz_help.get("short")
    if aaz_help.get("lines"):
        proto_help.long = "\n".join(aaz_help.get("lines"))
    return proto_help


def convert_aaz_arg_help_to_proto(aaz_help):
    proto_help = argument_pb2.CrsArgHelp()
    if aaz_help.get("short"):
        proto_help.short = aaz_help.get("short")
    if aaz_help.get("lines"):
        proto_help.long = "\n".join(aaz_help.get("lines"))
    return proto_help


def convert_aaz_command_group_to_proto(aaz_group, resouce_latest_versions_map):
    global command_num
    proto_group = command_pb2.CrsCommandGroup()
    proto_group.name = aaz_group.names[-1]
    proto_group.uri = (
        f"crs://azure/{'/'.join(aaz_group.names)}/"
        if aaz_group.names
        else "crs://azure/"
    )

    if aaz_group.help:
        proto_group.help.CopyFrom(convert_aaz_help_to_proto(aaz_group.help))

    if hasattr(aaz_group, "command_groups") and aaz_group.command_groups:
        for group_name, subgroup in aaz_group.command_groups.items():
            proto_subgroup = convert_aaz_command_group_to_proto(
                subgroup, resouce_latest_versions_map
            )
            proto_group.groups.append(proto_subgroup)

    if hasattr(aaz_group, "commands") and aaz_group.commands:
        for cmd_name, command in aaz_group.commands.items():
            command_num = command_num + 1
            proto_command = convert_aaz_command_to_proto(
                command, resouce_latest_versions_map
            )
            if proto_command:
                proto_group.commands.append(proto_command)

    return proto_group


def convert_aaz_resource_to_proto(aaz_resource):
    proto_resource = resource_pb2.CrsRestResource()
    proto_resource.id = getattr(aaz_resource, "id", "unknown")
    proto_resource.version = getattr(aaz_resource, "version", "unknown")
    proto_resource.plane = getattr(aaz_resource, "plane", "unknown")
    if hasattr(aaz_resource, "subresource") and aaz_resource.subresource:
        proto_resource.subresource = aaz_resource.subresource
    return proto_resource


def convert_aaz_command_to_proto(aaz_command, resource_latest_versions_map):
    proto_command = command_pb2.CrsCommand()
    proto_command.name = aaz_command.names[-1]
    proto_command.uri = (
        f"crs://azure/{'/'.join(aaz_command.names)}"
        if aaz_command.names
        else "crs://azure/"
    )

    print(f"Processing command: {proto_command.name} with URI: {proto_command.uri}")

    command_latest_version = (
        aaz_command.versions[-1]
        if aaz_command.versions and hasattr(aaz_command, "versions")
        else None
    )
    if not command_latest_version:
        raise ValueError(
            f"Command {proto_command.name} does not have any versions defined."
        )

    if (
        not hasattr(command_latest_version, "resources")
        or not command_latest_version.resources
        or not hasattr(command_latest_version.resources[0], "id")
    ):
        raise ValueError(
            f"Command {command_latest_version.name} does not have valid resources or resource IDs."
        )

    resource_id = command_latest_version.resources[0].id

    resource_in_map = resource_latest_versions_map.get(resource_id, None)
    if not resource_in_map:
        logging.warning(
            f"Resource ID {resource_id} not found in the latest versions map. Command {command_latest_version.name} may not be using the latest resource version."
        )
        command_name = "/".join(aaz_command.names) if aaz_command.names else "unknown"
        outdated_version_tracker.record_outdated_command(
            command_name=command_name,
            command_version=command_latest_version.name,
            latest_version="unknown_latest_version",
            resource_id=resource_id,
        )
        return None
    latest_version_for_resource = resource_in_map.get("latest_version", None)

    if (
        not latest_version_for_resource
        or command_latest_version.name != latest_version_for_resource
    ):
        logging.warning(
            f"Command {command_latest_version.name} is not using the latest resource version: {latest_version_for_resource}"
        )
        command_name = (
            "/".join(aaz_command.names) if aaz_command.names else "unknown_command"
        )
        outdated_version_tracker.record_outdated_command(
            command_name=command_name,
            command_version=command_latest_version.name,
            latest_version=latest_version_for_resource,
            resource_id=resource_id,
        )

    proto_command.version = command_latest_version.name

    specs_manager = AAZSpecsManager()
    cfg_reader = specs_manager.load_resource_cfg_reader_by_command_with_version(
        aaz_command, version=command_latest_version.name
    )
    if not cfg_reader:
        logging.warning(
            f"No configuration reader found for command {command_latest_version.name}"
        )
        return
    cmd_cfg = cfg_reader.find_command(*aaz_command.names)
    if not cmd_cfg:
        raise ValueError(
            f"No command configuration found for {'/'.join(aaz_command.names)}"
        )

    cmd_cfg_json = cmd_cfg.to_primitive()

    # # Debug: save the complete command to a proper location
    # cfg_dir = 'C:\\Users\\shiyingchen\\aaz-cirrus\\debug'
    # if not os.path.exists(cfg_dir):
    #     os.makedirs(cfg_dir)
    # cfg_file = os.path.join(cfg_dir, f"{'_'.join(aaz_command.names)}.json")
    # with open(cfg_file, 'w', encoding='utf-8') as f:
    #     json.dump(cmd_cfg_json, f, indent=2, ensure_ascii=False)
    # print(f"Command configuration saved to: {cfg_file}")

        
    # # Read cmd_cfg_json from debug folder
    # cfg_dir = 'C:\\Users\\shiyingchen\\aaz-cirrus\\debug'
    # cfg_file = os.path.join(cfg_dir, f"{'_'.join(aaz_command.names)}.json")
    
    # if os.path.exists(cfg_file):
    #     try:
    #         with open(cfg_file, 'r', encoding='utf-8') as f:
    #             cmd_cfg_json = json.load(f)
    #         logging.info(f"Loaded command configuration from: {cfg_file}")
    #     except (json.JSONDecodeError, IOError) as e:
    #         logging.error(f"Failed to load command configuration from {cfg_file}: {e}")
    #         return
    # else:
    #     logging.error(f"Command configuration file not found: {cfg_file}")
    #     return

    if cmd_cfg_json.get("help"):
        help_data = cmd_cfg_json["help"]
        proto_command.help.CopyFrom(convert_aaz_help_to_proto(help_data))
    if cmd_cfg_json.get("confirmation"):
        proto_command.confirmation = cmd_cfg_json["confirmation"]
    if cmd_cfg_json.get("argGroups"):
        for aaz_arggrp in cmd_cfg_json["argGroups"]:
            arg_group_name = aaz_arggrp.get("name", "")
            if aaz_arggrp.get("args"):
                for aaz_arg in aaz_arggrp["args"]:
                    proto_arg = convert_aaz_arg_to_proto(arg_group_name, aaz_arg)
                    proto_command.args.append(proto_arg)

    if cmd_cfg_json.get("positionalArgs"):
        proto_command.positional_args.extend(cmd_cfg_json["positionalArgs"])

    plugin_model = model_pb2.CrsPluginModelCommand()

    for aaz_resource in command_latest_version.resources:
        proto_resource = convert_aaz_resource_to_proto(aaz_resource)
        plugin_model.resources.append(proto_resource)
    if cmd_cfg_json.get("operations"):
        for aaz_operation_data in cmd_cfg_json["operations"]:
            proto_operation = convert_aaz_operation_to_proto(aaz_operation_data)
            plugin_model.operations.append(proto_operation)
    if cmd_cfg_json.get("outputs"):
        for aaz_output_data in cmd_cfg_json["outputs"]:
            proto_output = convert_aaz_output_to_proto(aaz_output_data)
            plugin_model.outputs.append(proto_output)
    if cmd_cfg_json.get("conditions"):
        for aaz_condition_data in cmd_cfg_json["conditions"]:
            proto_condition = convert_aaz_condition_to_proto(aaz_condition_data)
            plugin_model.conditions.append(proto_condition)
    if cmd_cfg_json.get("subresourceSelector"):
        proto_selector = convert_aaz_selector_to_proto(cmd_cfg_json["subresourceSelector"])
        plugin_model.subresource_selector.CopyFrom(proto_selector)
    proto_command.model.CopyFrom(plugin_model)
    return proto_command


def convert_aaz_arg_to_proto(aaz_arg_group_name, aaz_arg):
    proto_arg = argument_pb2.CrsArg()
    var_name = aaz_arg.get("var", "")
    proto_arg.var_name = var_name
    proto_arg.name = var_name.split(".")[-1] if var_name else aaz_arg.get("name", "")
    if aaz_arg.get("options"):
        proto_arg.options.extend(aaz_arg["options"])
    proto_arg.group = aaz_arg_group_name
    proto_arg.internal = aaz_arg.get("internal", False)
    proto_arg.required = aaz_arg.get("required", False)
    proto_arg.nullable = aaz_arg.get("nullable", False)
    if aaz_arg.get("help"):
        proto_arg.help.CopyFrom(convert_aaz_arg_help_to_proto(aaz_arg["help"]))
    if aaz_arg.get("blank"):
        proto_arg.blank.value = json.dumps(aaz_arg["blank"])
    if aaz_arg.get("default"):
        proto_arg.default.value = json.dumps(aaz_arg["default"])
    if aaz_arg.get("prompt"):
        prompt_data = aaz_arg["prompt"]
        proto_arg.prompt.prompt = prompt_data.get("msg", "")
        proto_arg.prompt.secret = prompt_data.get("secret", False)
        proto_arg.prompt.confirm = prompt_data.get("confirm", False)
    arg_type = aaz_arg.get("type", None)
    if arg_type is None or arg_type == "any":
        proto_arg.any_type.CopyFrom(argument_pb2.CrsAnyTypeArg())
    elif arg_type == "string":
        string_arg = argument_pb2.CrsStringArg()
        format_data = aaz_arg.get("format", None)
        if format_data:
            str_format = argument_pb2.CrsStringFormat()
            if format_data.get("pattern"):
                str_format.pattern = format_data.get("pattern")
            if format_data.get("maxLength") is not None:
                str_format.max_length = format_data.get("maxLength")
            if format_data.get("minLength") is not None:
                str_format.min_length = format_data.get("minLength")
            string_arg.string.CopyFrom(str_format)
        if aaz_arg.get("enum"):
            enum_data = aaz_arg.get("enum")
            if enum_data.get("items") and isinstance(enum_data["items"], list):
                for item in enum_data["items"]:
                    enum_item = string_arg.enum.items.add()
                    enum_item.name = item.get("name", "")
                    enum_item.value = json.dumps(item.get("value", ""))
                    enum_item.internal = item.get("internal", False)
            string_arg.enum.support_extension = enum_data.get("supportExtension", False)
            string_arg.enum.case_sensitive = enum_data.get("caseSensitive", False)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "binary":
        string_arg = argument_pb2.CrsStringArg()
        binary_format = argument_pb2.CrsBinaryFormat()
        string_arg.binary.CopyFrom(binary_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "byte":
        string_arg = argument_pb2.CrsStringArg()
        byte_format = argument_pb2.CrsByteFormat()
        string_arg.byte.CopyFrom(byte_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "duration":
        string_arg = argument_pb2.CrsStringArg()
        duration_format = argument_pb2.CrsDurationFormat()
        if aaz_arg.get("protocol"):
            duration_format.protocol = aaz_arg["protocol"]
        string_arg.duration.CopyFrom(duration_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "date":
        string_arg = argument_pb2.CrsStringArg()
        date_format = argument_pb2.CrsDateFormat()
        if aaz_arg.get("protocol"):
            date_format.protocol = aaz_arg["protocol"]
        string_arg.date.CopyFrom(date_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "dateTime":
        string_arg = argument_pb2.CrsStringArg()
        datetime_format = argument_pb2.CrsDateTimeFormat()
        if aaz_arg.get("protocol"):
            datetime_format.protocol = aaz_arg["protocol"]
        string_arg.date_time.CopyFrom(datetime_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "time":
        string_arg = argument_pb2.CrsStringArg()
        time_format = argument_pb2.CrsTimeFormat()
        if aaz_arg.get("protocol"):
            time_format.protocol = aaz_arg["protocol"]
        string_arg.time.CopyFrom(time_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "uuid":
        string_arg = argument_pb2.CrsStringArg()
        uuid_format = argument_pb2.CrsUuidFormat()
        if aaz_arg.get("case"):
            uuid_format.case = aaz_arg["case"]
        if aaz_arg.get("noHyphen"):
            uuid_format.no_hyphen = aaz_arg["noHyphen"]
        if aaz_arg.get("withBraces"):
            uuid_format.no_braces = aaz_arg["withBraces"]
        string_arg.uuid.CopyFrom(uuid_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "password":
        string_arg = argument_pb2.CrsStringArg()
        string_arg.password.CopyFrom(argument_pb2.CrsPasswordFormat())
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "SubscriptionId":
        string_arg = argument_pb2.CrsStringArg()
        string_arg.subscription_id.CopyFrom(argument_pb2.CrsSubscriptionIdFormat())
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "ResourceGroupName":
        string_arg = argument_pb2.CrsStringArg()
        string_arg.resource_group_name.CopyFrom(
            argument_pb2.CrsResourceGroupNameFormat()
        )
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "ResourceId":
        string_arg = argument_pb2.CrsStringArg()
        resource_id_format = argument_pb2.CrsResourceIdFormat()
        if aaz_arg.get("template"):
            templates = aaz_arg.get("template")
            if isinstance(templates, list):
                resource_id_format.templates.extend(templates)
            else:
                resource_id_format.templates.append(templates)
        string_arg.resource_id.CopyFrom(resource_id_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "ResourceLocation":
        string_arg = argument_pb2.CrsStringArg()
        location_format = argument_pb2.CrsResourceLocationFormat()
        location_format.no_rg_default = aaz_arg.get("noRgDefault", False)
        string_arg.resource_location.CopyFrom(location_format)
        proto_arg.string.CopyFrom(string_arg)
    elif arg_type == "boolean":
        boolean_arg = argument_pb2.CrsBooleanArg()
        if aaz_arg.get("reverseOptions"):
            boolean_arg.reverse_options.extend(aaz_arg.get("reverseOptions"))
        proto_arg.boolean.CopyFrom(boolean_arg)
    elif arg_type in [
        "integer",
        "integer32",
        "integer64",
        "uint32",
        "uint64",
        "float",
        "float32",
        "float64",
        "double",
    ]:
        number_arg = argument_pb2.CrsNumberArg()
        if aaz_arg.get("enum"):
            enum_data = aaz_arg.get("enum")
            if enum_data.get("items") and isinstance(enum_data["items"], list):
                for item in enum_data["items"]:
                    enum_item = number_arg.enum.items.add()
                    enum_item.name = item.get("name", "")
                    enum_item.value = json.dumps(item.get("value", ""))
                    enum_item.internal = item.get("internal", False)
            number_arg.enum.support_extension = enum_data.get("supportExtension", False)
            number_arg.enum.case_sensitive = enum_data.get("caseSensitive", False)
        format_data = aaz_arg.get("format", {})
        if arg_type == "integer" or arg_type == "integer32":
            int32_format = argument_pb2.CrsInt32Format()
            if format_data.get("minimum") is not None:
                int32_format.minimum = format_data.get("minimum")
            if format_data.get("maximum") is not None:
                int32_format.maximum = format_data.get("maximum")
            if format_data.get("multipleOf") is not None:
                int32_format.multiple_of = format_data.get("multipleOf")
            number_arg.int32.CopyFrom(int32_format)
        elif arg_type == "integer64":
            int64_format = argument_pb2.CrsInt64Format()
            if format_data.get("minimum") is not None:
                int64_format.minimum = format_data.get("minimum")
            if format_data.get("maximum") is not None:
                int64_format.maximum = format_data.get("maximum")
            if format_data.get("multipleOf") is not None:
                int64_format.multiple_of = format_data.get("multipleOf")
            number_arg.int64.CopyFrom(int64_format)
        elif arg_type == "uint32":
            uint32_format = argument_pb2.CrsUint32Format()
            if format_data.get("minimum") is not None:
                uint32_format.minimum = format_data.get("minimum")
            if format_data.get("maximum") is not None:
                uint32_format.maximum = format_data.get("maximum")
            if format_data.get("multipleOf") is not None:
                uint32_format.multiple_of = format_data.get("multipleOf")
            number_arg.uint32.CopyFrom(uint32_format)
        elif arg_type == "uint64":
            uint64_format = argument_pb2.CrsUint64Format()
            if format_data.get("minimum") is not None:
                uint64_format.minimum = format_data.get("minimum")
            if format_data.get("maximum") is not None:
                uint64_format.maximum = format_data.get("maximum")
            if format_data.get("multipleOf") is not None:
                uint64_format.multiple_of = format_data.get("multipleOf")
            number_arg.uint64.CopyFrom(uint64_format)
        elif arg_type == "float" or arg_type == "float32":
            float_format = argument_pb2.CrsFloatFormat()
            if format_data.get("minimum") is not None:
                float_format.minimum = format_data.get("minimum")
            if format_data.get("maximum") is not None:
                float_format.maximum = format_data.get("maximum")
            if format_data.get("multipleOf") is not None:
                float_format.multiple_of = format_data.get("multipleOf")
            if format_data.get("exclusiveMinimum") is not None:
                float_format.exclusive_minimum = format_data.get("exclusiveMinimum")
            if format_data.get("exclusiveMaximum") is not None:
                float_format.exclusive_maximum = format_data.get("exclusiveMaximum")
            number_arg.float.CopyFrom(float_format)
        elif arg_type == "float64" or arg_type == "double":
            double_format = argument_pb2.CrsDoubleFormat()
            if format_data.get("minimum") is not None:
                double_format.minimum = format_data.get("minimum")
            if format_data.get("maximum") is not None:
                double_format.maximum = format_data.get("maximum")
            if format_data.get("multipleOf") is not None:
                double_format.multiple_of = format_data.get("multipleOf")
            if format_data.get("exclusiveMinimum") is not None:
                double_format.exclusive_minimum = format_data.get("exclusiveMinimum")
            if format_data.get("exclusiveMaximum") is not None:
                double_format.exclusive_maximum = format_data.get("exclusiveMaximum")
            number_arg.double.CopyFrom(double_format)
        proto_arg.number.CopyFrom(number_arg)
    elif arg_type == "object":
        object_arg = argument_pb2.CrsObjectArg()
        if aaz_arg.get("cls"):
            object_arg.cls_type = aaz_arg.get("cls")
        object_arg.ps_flatten = aaz_arg.get("psFlatten", False)
        format_data = aaz_arg.get("format", {})
        object_format = argument_pb2.CrsObjectFormat()
        if format_data.get("minLength") is not None:
            object_format.min_length = format_data.get("minLength")
        elif aaz_arg.get("minLength") is not None:
            object_format.min_length = aaz_arg.get("minLength")
        if format_data.get("maxLength") is not None:
            object_format.max_length = format_data.get("maxLength")
        elif aaz_arg.get("maxLength") is not None:
            object_format.max_length = aaz_arg.get("maxLength")
        object_arg.format.CopyFrom(object_format)
        if aaz_arg.get("props"):
            aaz_props = aaz_arg.get("props")
            for aaz_prop in aaz_props:
                prop = object_arg.props.add()
                prop.CopyFrom(convert_aaz_arg_to_proto(aaz_arg_group_name, aaz_prop))
        if aaz_arg.get("additionalProps"):
            aaz_additional_props = aaz_arg.get("additionalProps")
            additional_props = argument_pb2.CrsObjectArgAdditionalProperties()
            aaz_item = aaz_additional_props.get("item", {})

            additional_props.item.CopyFrom(
                convert_aaz_arg_to_proto(aaz_arg_group_name, aaz_item)
            )
            object_arg.additional_props.CopyFrom(additional_props)
        proto_arg.object.CopyFrom(object_arg)
    elif arg_type and arg_type.startswith("array<") and arg_type.endswith(">"):
        array_item_type = arg_type[6:-1]
        array_arg = argument_pb2.CrsArrayArg()
        if aaz_arg.get("cls"):
            array_arg.cls_type = aaz_arg.get("cls")
        format_data = aaz_arg.get("format", {})
        array_format = argument_pb2.CrsArrayFormat()
        array_format.unique = aaz_arg.get("unique", False)
        if format_data.get("minLength") is not None:
            array_format.min_length = format_data.get("minLength")
        elif aaz_arg.get("minLength") is not None:
            array_format.min_length = aaz_arg.get("minLength")
        if format_data.get("maxLength") is not None:
            array_format.max_length = format_data.get("maxLength")
        elif aaz_arg.get("maxLength") is not None:
            array_format.max_length = aaz_arg.get("maxLength")
        array_arg.format.CopyFrom(array_format)
        if aaz_arg.get("item"):
            aaz_item = aaz_arg.get("item")
            array_arg.item.CopyFrom(
                convert_aaz_arg_to_proto(aaz_arg_group_name, aaz_item)
            )
        elif array_item_type:
            aaz_item = {"type": array_item_type}
            array_arg.item.CopyFrom(
                convert_aaz_arg_to_proto(aaz_arg_group_name, aaz_item)
            )
        proto_arg.array.CopyFrom(array_arg)
    elif arg_type == "cls" or arg_type.startswith("@"):
        cls_arg = argument_pb2.CrsClsArg()
        if aaz_arg.get("cls"):
            cls_arg.cls_type = aaz_arg.get("cls")
        elif arg_type.startswith("@"):
            cls_arg.cls_type = arg_type[1:]
        proto_arg.cls.CopyFrom(cls_arg)
    else:
        proto_arg.any_type.CopyFrom(argument_pb2.CrsAnyTypeArg())

    return proto_arg


def convert_aaz_operation_to_proto(aaz_operation_data):
    proto_operation = operation_pb2.CrsOperation()

    if aaz_operation_data.get("when"):
        conditions = aaz_operation_data["when"]
        if isinstance(conditions, list):
            proto_operation.conditions.extend(conditions)
        elif isinstance(conditions, str):
            proto_operation.conditions.append(conditions)

    if aaz_operation_data.get("http"):
        http_op = operation_pb2.CrsHttpOperation()
        http_data = aaz_operation_data["http"]
        aaz_operation_id = aaz_operation_data.get("operationId", "")
        http_op.operation_id = aaz_operation_id
        http_action = convert_aaz_http_action_to_proto(http_data)
        http_op.action.CopyFrom(http_action)

        if aaz_operation_data.get("longRunning"):
            long_running = operation_pb2.CrsHttpOperationLongRunning()
            lr_data = aaz_operation_data["longRunning"]
            final_state_via = lr_data.get("finalStateVia", "azure-async-operation")

            if final_state_via == "azure-async-operation":
                long_running.final_state_via = long_running.StateVia.azureAsyncOperation
            elif final_state_via == "location":
                long_running.final_state_via = long_running.StateVia.location
            elif final_state_via == "original-uri":
                long_running.final_state_via = long_running.StateVia.originalUri
            else:
                long_running.final_state_via = long_running.StateVia.azureAsyncOperation

            http_op.long_running.CopyFrom(long_running)

            proto_operation.http.CopyFrom(http_op)

    elif aaz_operation_data.get("instanceCreate"):
        instance_create_op = operation_pb2.CrsInstanceCreateOperation()
        instance_create_data = aaz_operation_data["instanceCreate"]

        create_action = operation_pb2.CrsInstanceCreateAction()
        create_action.ref = instance_create_data.get("ref", "")

        if instance_create_data.get("json"):
            request_json = http_pb2.CrsRequestJson()
            json_data = instance_create_data["json"]
            if json_data.get("ref"):
                request_json.ref = json_data["ref"]
            if json_data.get("schema"):
                request_json.schema.CopyFrom(
                    convert_aaz_schema_to_proto(json_data["schema"])
                )
            create_action.json.CopyFrom(request_json)

        instance_create_op.instance_create.CopyFrom(create_action)
        proto_operation.instance_create.CopyFrom(instance_create_op)

    elif aaz_operation_data.get("instanceUpdate"):
        instance_update_op = operation_pb2.CrsInstanceUpdateOperation()
        instance_update_data = aaz_operation_data["instanceUpdate"]

        update_action = operation_pb2.CrsInstanceUpdateAction()
        update_action.ref = instance_update_data.get("ref", "")

        if instance_update_data.get("json"):
            request_json = http_pb2.CrsRequestJson()
            json_data = instance_update_data["json"]
            if json_data.get("ref"):
                request_json.ref = json_data["ref"]
            if json_data.get("schema"):
                request_json.schema.CopyFrom(
                    convert_aaz_schema_to_proto(json_data["schema"])
                )
            update_action.json.CopyFrom(request_json)

        instance_update_op.instance_update.CopyFrom(update_action)
        proto_operation.instance_update.CopyFrom(instance_update_op)

    elif aaz_operation_data.get("instanceDelete"):
        instance_delete_op = operation_pb2.CrsInstanceDeleteOperation()
        instance_delete_data = aaz_operation_data["instanceDelete"]

        delete_action = operation_pb2.CrsInstanceDeleteAction()
        delete_action.ref = instance_delete_data.get("ref", "")

        if instance_delete_data.get("json"):
            request_json = http_pb2.CrsRequestJson()
            json_data = instance_delete_data["json"]
            if json_data.get("ref"):
                request_json.ref = json_data["ref"]
            if json_data.get("schema"):
                request_json.schema.CopyFrom(
                    convert_aaz_schema_to_proto(json_data["schema"])
                )
            delete_action.json.CopyFrom(request_json)

        instance_delete_op.instance_delete.CopyFrom(delete_action)
        proto_operation.instance_delete.CopyFrom(instance_delete_op)

    return proto_operation


def convert_aaz_http_action_to_proto(aaz_action_data):
    proto_action = http_pb2.CrsHttpAction()
    proto_action.path = aaz_action_data.get("path", "")

    if aaz_action_data.get("request"):
        proto_request = convert_aaz_http_request_to_proto(aaz_action_data["request"])
        proto_action.request.CopyFrom(proto_request)

    if aaz_action_data.get("responses"):
        for response_data in aaz_action_data["responses"]:
            proto_response = convert_aaz_http_response_to_proto(response_data)
            proto_action.responses.append(proto_response)

    return proto_action


def convert_aaz_schema_to_proto(aaz_schema_data):
    proto_schema = schema_pb2.CrsSchema()

    proto_schema.read_only = aaz_schema_data.get("readOnly", False)
    proto_schema.const = aaz_schema_data.get("const", False)
    proto_schema.nullable = aaz_schema_data.get("nullable", False)

    if (
        aaz_schema_data.get("name")
        or aaz_schema_data.get("arg")
        or aaz_schema_data.get("required") is not None
    ):
        info = schema_pb2.CrsSchemaInfo()
        info.name = aaz_schema_data.get("name", "")
        if aaz_schema_data.get("arg"):
            info.arg = aaz_schema_data["arg"]
        info.required = aaz_schema_data.get("required", False)
        info.skip_url_encoding = aaz_schema_data.get("skipUrlEncoding", False)
        info.secret = aaz_schema_data.get("secret", False)
        proto_schema.info.CopyFrom(info)

    schema_type = aaz_schema_data.get("type", "string")

    if schema_type is None or schema_type == "any":
        proto_schema.any_type.CopyFrom(schema_pb2.CrsAnyTypeSchema())
    elif (
        schema_type == "cls"
        or aaz_schema_data.get("cls")
        or schema_type.startswith("@")
    ):
        cls_schema = schema_pb2.CrsClsSchema()
        if aaz_schema_data.get("cls"):
            cls_schema.cls_type = aaz_schema_data["cls"]
        elif schema_type.startswith("@"):
            cls_schema.cls_type = schema_type[1:]
        cls_schema.client_flatten = aaz_schema_data.get("clientFlatten", False)
        proto_schema.cls.CopyFrom(cls_schema)
    elif schema_type in [
        "string",
        "binary",
        "byte",
        "duration",
        "date",
        "dateTime",
        "time",
        "uuid",
        "password",
        "SubscriptionId",
        "ResourceGroupName",
        "ResourceId",
        "ResourceLocation",
    ]:
        proto_schema.string.CopyFrom(schema_pb2.CrsStringSchema())
    elif schema_type in ["integer", "integer32", "integer64"]:
        proto_schema.integer.CopyFrom(schema_pb2.CrsIntegerSchema())
    elif schema_type in ["float", "float32", "float64"]:
        proto_schema.float.CopyFrom(schema_pb2.CrsFloatSchema())
    elif schema_type == "boolean":
        proto_schema.boolean.CopyFrom(schema_pb2.CrsBooleanSchema())
    elif schema_type in ["object", "IdentityObject"]:
        obj_schema = schema_pb2.CrsObjectSchema()
        if aaz_schema_data.get("cls"):
            obj_schema.cls = aaz_schema_data["cls"]
        obj_schema.client_flatten = aaz_schema_data.get("clientFlatten", False)

        if aaz_schema_data.get("props"):
            for prop_data in aaz_schema_data["props"]:
                prop_schema = convert_aaz_schema_to_proto(prop_data)
                obj_schema.props.append(prop_schema)

        if aaz_schema_data.get("discriminators"):
            for disc_data in aaz_schema_data["discriminators"]:
                discriminator = schema_pb2.CrsObjectSchemaDiscriminator()
                discriminator.property = disc_data.get("property", "")
                discriminator.value = disc_data.get("value", "")
                if disc_data.get("props"):
                    for prop_data in disc_data["props"]:
                        prop_schema = convert_aaz_schema_to_proto(prop_data)
                        discriminator.props.append(prop_schema)
                obj_schema.discriminators.append(discriminator)

        if aaz_schema_data.get("additionalProps"):
            add_props = schema_pb2.CrsObjectSchemaAdditionalProperties()
            add_props_data = aaz_schema_data["additionalProps"]
            add_props.read_only = add_props_data.get("readOnly", False)
            if add_props_data.get("item"):
                add_props.item.CopyFrom(
                    convert_aaz_schema_to_proto(add_props_data["item"])
                )
            obj_schema.additional_props.CopyFrom(add_props)
        proto_schema.object.CopyFrom(obj_schema)

    elif schema_type == "array":
        array_schema = schema_pb2.CrsArraySchema()
        if aaz_schema_data.get("cls"):
            array_schema.cls = aaz_schema_data["cls"]
        if aaz_schema_data.get("item"):
            array_schema.item.CopyFrom(
                convert_aaz_schema_to_proto(aaz_schema_data["item"])
            )
        proto_schema.array.CopyFrom(array_schema)
    else:
        proto_schema.any_type.CopyFrom(schema_pb2.CrsAnyTypeSchema())

    return proto_schema


def convert_aaz_http_request_to_proto(aaz_request_data):
    proto_request = http_pb2.CrsHttpRequest()

    method_map = {
        "GET": http_pb2.CrsHttpRequest.GET,
        "POST": http_pb2.CrsHttpRequest.POST,
        "PUT": http_pb2.CrsHttpRequest.PUT,
        "DELETE": http_pb2.CrsHttpRequest.DELETE,
        "PATCH": http_pb2.CrsHttpRequest.PATCH,
        "HEAD": http_pb2.CrsHttpRequest.HEAD,
        "OPTIONS": http_pb2.CrsHttpRequest.OPTIONS,
    }

    method = aaz_request_data.get("method", "GET")
    proto_request.method = method_map.get(method.upper(), http_pb2.CrsHttpRequest.GET)

    if aaz_request_data.get("path"):
        path_data = aaz_request_data["path"]
        path_proto = http_pb2.CrsHttpRequestPath()

        if path_data.get("params"):
            for param_data in path_data["params"]:
                param_schema = convert_aaz_schema_to_proto(param_data)
                path_proto.params.append(param_schema)

        if path_data.get("consts"):
            for const_data in path_data["consts"]:
                const_schema = convert_aaz_schema_to_proto(const_data)
                path_proto.consts.append(const_schema)

        proto_request.path.CopyFrom(path_proto)

    if aaz_request_data.get("query"):
        query_data = aaz_request_data["query"]
        query_proto = http_pb2.CrsHttpRequestQuery()

        if query_data.get("params"):
            for param_data in query_data["params"]:
                param_schema = convert_aaz_schema_to_proto(param_data)
                query_proto.params.append(param_schema)

        if query_data.get("consts"):
            for const_data in query_data["consts"]:
                const_schema = convert_aaz_schema_to_proto(const_data)
                query_proto.consts.append(const_schema)

        proto_request.query.CopyFrom(query_proto)

    if aaz_request_data.get("header"):
        header_data = aaz_request_data["header"]
        header_proto = http_pb2.CrsHttpRequestHeader()

        if header_data.get("params"):
            for param_data in header_data["params"]:
                param_schema = convert_aaz_schema_to_proto(param_data)
                header_proto.params.append(param_schema)

        if header_data.get("consts"):
            for const_data in header_data["consts"]:
                const_schema = convert_aaz_schema_to_proto(const_data)
                header_proto.consts.append(const_schema)

        if header_data.get("clientRequestId"):
            header_proto.client_request_id = header_data["clientRequestId"]

        proto_request.header.CopyFrom(header_proto)

    if aaz_request_data.get("body"):
        body_data = aaz_request_data["body"]
        if body_data.get("json"):
            json_body = http_pb2.CrsHttpRequestJsonBody()
            request_json = http_pb2.CrsRequestJson()

            json_data = body_data["json"]
            if json_data.get("ref"):
                request_json.ref = json_data["ref"]
            if json_data.get("schema"):
                request_json.schema.CopyFrom(
                    convert_aaz_schema_to_proto(json_data["schema"])
                )

            json_body.json.CopyFrom(request_json)
            proto_request.json.CopyFrom(json_body)

    return proto_request


def convert_aaz_http_response_to_proto(aaz_response_data):
    proto_response = http_pb2.CrsHttpResponse()

    status_codes = aaz_response_data.get("statusCode") or aaz_response_data.get(
        "statusCodes"
    )
    if status_codes:
        if isinstance(status_codes, list):
            for code in status_codes:
                if isinstance(code, list):
                    proto_response.status_codes.extend([int(c) for c in code])
                else:
                    proto_response.status_codes.append(int(code))
        elif isinstance(status_codes, (int, str)):
            proto_response.status_codes.append(int(status_codes))

    proto_response.is_error = aaz_response_data.get("isError", False)

    if aaz_response_data.get("headers"):
        header_data = aaz_response_data["headers"]
        response_header = http_pb2.CrsHttpResponseHeader()

        if isinstance(header_data, list):
            for header_item_data in header_data:
                header_item = http_pb2.CrsHttpResponseHeaderItem()
                header_item.name = header_item_data.get("name", "")
                if header_item_data.get("var"):
                    header_item.var = header_item_data["var"]
                response_header.items.append(header_item)
        elif isinstance(header_data, dict):
            for name, var in header_data.items():
                header_item = http_pb2.CrsHttpResponseHeaderItem()
                header_item.name = name
                if var:
                    header_item.var = var
                response_header.items.append(header_item)

        proto_response.header.CopyFrom(response_header)

    if aaz_response_data.get("body"):
        body_data = aaz_response_data["body"]
        if body_data.get("json"):
            json_body = http_pb2.CrsHttpResponseJsonBody()
            response_json = http_pb2.CrsResponseJson()

            json_data = body_data["json"]
            if json_data.get("var"):
                response_json.var = json_data["var"]
            if json_data.get("schema"):
                response_json.schema.CopyFrom(
                    convert_aaz_schema_to_proto(json_data["schema"])
                )

            json_body.json.CopyFrom(response_json)
            proto_response.json.CopyFrom(json_body)

    return proto_response


def convert_aaz_output_to_proto(aaz_output_data):
    proto_output = output_pb2.CrsOutput()

    aaz_output_type = aaz_output_data.get("type")

    if aaz_output_type == "object":
        obj_output = output_pb2.CrsObjectOutput()
        obj_output.ref = aaz_output_data.get("ref", "")
        obj_output.client_flatten = aaz_output_data.get("clientFlatten", False)
        proto_output.object.CopyFrom(obj_output)

    elif aaz_output_type == "array":
        array_output = output_pb2.CrsArrayOutput()
        array_output.ref = aaz_output_data.get("ref", "")
        array_output.client_flatten = aaz_output_data.get("clientFlatten", False)
        if aaz_output_data.get("next_link") or aaz_output_data.get("nextLink"):
            array_output.next_link = aaz_output_data.get(
                "next_link", aaz_output_data.get("nextLink", "")
            )
        proto_output.array.CopyFrom(array_output)

    elif aaz_output_type == "string":
        string_output = output_pb2.CrsStringOutput()

        if aaz_output_data.get("ref"):
            string_output.ref = aaz_output_data["ref"]
        elif aaz_output_data.get("value"):
            string_output.value = aaz_output_data["value"]

        proto_output.string.CopyFrom(string_output)

    return proto_output


def convert_aaz_condition_operator_to_proto(aaz_operator_data):
    proto_operator = condition_pb2.CrsConditionOperator()

    operator_type = aaz_operator_data.get("type")

    if operator_type == "hasValue":
        has_value_op = condition_pb2.CrsConditionHasValueOperator()
        has_value_op.arg = aaz_operator_data.get("arg", "")
        proto_operator.has_value.CopyFrom(has_value_op)

    elif operator_type == "and":
        and_op = condition_pb2.CrsConditionAndOperator()
        operators_data = aaz_operator_data.get("operators", [])
        for nested_operator_data in operators_data:
            nested_operator = convert_aaz_condition_operator_to_proto(
                nested_operator_data
            )
            and_op.operators.append(nested_operator)
        getattr(proto_operator, "and").CopyFrom(and_op)

    elif operator_type == "or":
        or_op = condition_pb2.CrsConditionOrOperator()
        operators_data = aaz_operator_data.get("operators", [])
        for nested_operator_data in operators_data:
            nested_operator = convert_aaz_condition_operator_to_proto(
                nested_operator_data
            )
            or_op.operators.append(nested_operator)
        getattr(proto_operator, "or").CopyFrom(or_op)

    elif operator_type == "not":
        not_op = condition_pb2.CrsConditionNotOperator()
        nested_operator_data = aaz_operator_data.get("operator")
        if nested_operator_data:
            nested_operator = convert_aaz_condition_operator_to_proto(
                nested_operator_data
            )
            not_op.operator.CopyFrom(nested_operator)
        getattr(proto_operator, "not").CopyFrom(not_op)

    return proto_operator


def convert_aaz_condition_to_proto(aaz_condition_data):
    proto_condition = condition_pb2.CrsCondition()

    proto_condition.var = aaz_condition_data.get("var", "")

    aaz_operator_data = aaz_condition_data.get("operator")
    if aaz_operator_data:
        proto_operator = convert_aaz_condition_operator_to_proto(aaz_operator_data)
        proto_condition.operator.CopyFrom(proto_operator)

    return proto_condition


def convert_aaz_selector_index_to_proto(aaz_index_data):
    proto_index = selector_pb2.CrsSelectorIndex()

    if aaz_index_data.get("name"):
        info = selector_pb2.CrsSelectorIndexInfo()
        info.name = aaz_index_data.get("name", "")
        proto_index.info.CopyFrom(info)

    index_type = aaz_index_data.get("type", "simple")

    if index_type == "object":
        object_index = selector_pb2.CrsObjectIndex()

        if aaz_index_data.get("prop"):
            prop_index = convert_aaz_selector_index_to_proto(aaz_index_data["prop"])
            object_index.prop.CopyFrom(prop_index)

        if aaz_index_data.get("discriminator"):
            discriminator = convert_aaz_object_discriminator_to_proto(
                aaz_index_data["discriminator"]
            )
            object_index.discriminator.CopyFrom(discriminator)

        if aaz_index_data.get("additional_props") or aaz_index_data.get(
            "additionalProps"
        ):
            add_props_data = aaz_index_data.get(
                "additional_props", aaz_index_data.get("additionalProps")
            )
            add_props = selector_pb2.CrsObjectIndexAdditionalProperties()

            if add_props_data.get("item"):
                item_index = convert_aaz_selector_index_to_proto(add_props_data["item"])
                add_props.item.CopyFrom(item_index)

            if add_props_data.get("identifiers"):
                for identifier_data in add_props_data["identifiers"]:
                    identifier_schema = convert_aaz_schema_to_proto(identifier_data)
                    add_props.identifiers.append(identifier_schema)

            object_index.additional_props.CopyFrom(add_props)

        proto_index.object.CopyFrom(object_index)

    elif index_type == "array":
        array_index = selector_pb2.CrsArrayIndex()

        if aaz_index_data.get("item"):
            item_index = convert_aaz_selector_index_to_proto(aaz_index_data["item"])
            array_index.item.CopyFrom(item_index)

        if aaz_index_data.get("identifiers"):
            for identifier_data in aaz_index_data["identifiers"]:
                identifier_schema = convert_aaz_schema_to_proto(identifier_data)
                array_index.identifiers.append(identifier_schema)

        proto_index.array.CopyFrom(array_index)

    else:
        simple_index = selector_pb2.CrsSimpleIndex()
        proto_index.simple.CopyFrom(simple_index)

    return proto_index


def convert_aaz_object_discriminator_to_proto(aaz_discriminator_data):
    proto_discriminator = selector_pb2.CrsObjectIndexDiscriminator()

    proto_discriminator.property = aaz_discriminator_data.get("property", "")
    proto_discriminator.value = aaz_discriminator_data.get("value", "")

    if aaz_discriminator_data.get("prop"):
        prop_index = convert_aaz_selector_index_to_proto(aaz_discriminator_data["prop"])
        proto_discriminator.prop.CopyFrom(prop_index)

    if aaz_discriminator_data.get("discriminator"):
        nested_discriminator = convert_aaz_object_discriminator_to_proto(
            aaz_discriminator_data["discriminator"]
        )
        proto_discriminator.discriminator.CopyFrom(nested_discriminator)

    return proto_discriminator


def convert_aaz_selector_to_proto(aaz_selector_data):
    proto_selector = selector_pb2.CrsSubresourceSelector()

    proto_selector.var = aaz_selector_data.get("var", "")
    proto_selector.ref = aaz_selector_data.get("ref", "")

    if aaz_selector_data.get("json"):
        json_data = aaz_selector_data["json"]
        selector_index = convert_aaz_selector_index_to_proto(json_data)
        proto_selector.json.CopyFrom(selector_index)

    return proto_selector
