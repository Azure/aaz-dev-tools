import click
import logging
from flask import Blueprint
import sys
import os
import json

from protos import component_pb2, command_pb2, argument_pb2
from protos.plugin import model_pb2, resource_pb2, operation_pb2, output_pb2, selector_pb2, condition_pb2, http_pb2, schema_pb2
from google.protobuf.json_format import ParseDict, MessageToJson
from command.controller.specs_manager import AAZSpecsManager
from utils.config import Config

logger = logging.getLogger('backend')

bp = Blueprint('cirrus-cmds', __name__, url_prefix='/CIRRUS/CMDs', cli_group="cirrus")
bp.cli.short_help = "Generate aaz models as cirrus components."

@bp.cli.command("export-component", short_help="Export aaz models as a cirrus component.")
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
    "--output-path", '-o',
    required=True,
    help="The output path where the component will be exported."
)
@click.option(
    "--component-name", '--name',
    required=True,
    help="Name of the component"
)
def export_component(component_name, output_path):
    print(f"Using AAZ path: {Config.AAZ_PATH}")    
    
    specs_manager = AAZSpecsManager()
    module_name = component_name.lower()
    component_uri = f"crs://azure/{module_name}/"
    
    print(f"Exporting component: {component_name} with URI: {component_uri}")

    def process_in_tree_format(root_module):
        def process_node(node):
            node_data = {
                "name": node.names[-1] if node.names else "unknown",
                "full_name": " ".join(node.names) if node.names else "",
                "help": node.help.short if node.help and node.help.short else None,
                "type": "command_group"
            }
            
            if hasattr(node, 'command_groups') and node.command_groups:
                node_data["command_groups"] = {}
                for group_name, group in sorted(node.command_groups.items()):
                    node_data["command_groups"][group_name] = process_node(group)
            
            if hasattr(node, 'commands') and node.commands:
                node_data["commands"] = {}
                for cmd_name, command in sorted(node.commands.items()):
                    command_data = {
                        "name": cmd_name,
                        "full_name": " ".join(command.names) if command.names else "",
                        "help": command.help.short if command.help and command.help.short else None,
                        "type": "command",
                        "latest_version": None
                    }
                    
                    if command.versions:
                        sorted_versions = sorted(command.versions, key=lambda v: v.name, reverse=True)
                        latest_version = sorted_versions[0]
                        
                        version_data = {
                            "name": latest_version.name,
                            "stage": getattr(latest_version, 'stage', None),
                            "resources": []
                        }
                        if hasattr(latest_version, 'resources') and latest_version.resources:
                            for resource in latest_version.resources:
                                resource_data = {
                                    "id": getattr(resource, 'id', None),
                                    "version": getattr(resource, 'version', None),
                                    "plane": getattr(resource, 'plane', None),
                                    "subresource": getattr(resource, 'subresource', None)
                                }
                                version_data["resources"].append(resource_data)
                        command_data["latest_version"] = version_data
                    
                    node_data["commands"][cmd_name] = command_data
            
            return node_data
        
        return process_node(root_module)

    root_module = specs_manager.find_command_group(module_name)
    if root_module:
        tree_json = process_in_tree_format(root_module)
        tree_json["module"] = module_name
        output_file = os.path.join(output_path, f"{module_name}_command_tree.json")
        os.makedirs(output_path, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tree_json, f, indent=2, ensure_ascii=False)
        print(f"Command tree JSON saved to: {output_file}")
        print(f"Found {len(tree_json.get('command_groups', {}))} command groups and {len(tree_json.get('commands', {}))} commands")
     
