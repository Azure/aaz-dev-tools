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

    def convert_aaz_resource_to_crs(aaz_resource):
        """Convert AAZ resource to protobuf CrsRestResource"""
        proto_resource = resource_pb2.CrsRestResource()
        proto_resource.id = getattr(aaz_resource, 'id', '')
        proto_resource.version = getattr(aaz_resource, 'version', '')
        proto_resource.plane = getattr(aaz_resource, 'plane', '')
        if hasattr(aaz_resource, 'subresource') and aaz_resource.subresource:
            proto_resource.subresource = aaz_resource.subresource
        return proto_resource

    def convert_aaz_command_to_crs(aaz_command):
        """Convert AAZ command to protobuf CrsCommand"""
        proto_command = command_pb2.CrsCommand()
        proto_command.name = " ".join(aaz_command.names) if aaz_command.names else ""
        proto_command.uri = f"{component_uri}{'/'.join(aaz_command.names)}" if aaz_command.names else component_uri
        
        # Get latest version
        if aaz_command.versions:
            sorted_versions = sorted(aaz_command.versions, key=lambda v: v.name, reverse=True)
            latest_version = sorted_versions[0]
            proto_command.version = latest_version.name
            
            # Set help information
            if aaz_command.help:
                proto_command.help.short = aaz_command.help.short or ""
                if aaz_command.help.lines:
                    proto_command.help.long = "\n".join(aaz_command.help.lines)
            
            # Create plugin model command
            plugin_model = model_pb2.CrsPluginModelCommand()
            
            # Add resources
            if hasattr(latest_version, 'resources') and latest_version.resources:
                for aaz_resource in latest_version.resources:
                    proto_resource = convert_aaz_resource_to_crs(aaz_resource)
                    plugin_model.resources.append(proto_resource)
            
            proto_command.model.CopyFrom(plugin_model)
        
        return proto_command

    def convert_aaz_command_group_to_proto(aaz_group):
        """Convert AAZ command group to protobuf CrsCommandGroup"""
        proto_group = command_pb2.CrsCommandGroup()
        proto_group.name = " ".join(aaz_group.names) if aaz_group.names else ""
        proto_group.uri = f"{component_uri}{'/'.join(aaz_group.names)}" if aaz_group.names else component_uri
        
        # Set help information
        if aaz_group.help:
            proto_group.help.short = aaz_group.help.short or ""
            if aaz_group.help.lines:
                proto_group.help.long = "\n".join(aaz_group.help.lines)
        
        # Add subgroups
        if hasattr(aaz_group, 'command_groups') and aaz_group.command_groups:
            for group_name, subgroup in aaz_group.command_groups.items():
                proto_subgroup = convert_aaz_command_group_to_proto(subgroup)
                proto_group.groups.append(proto_subgroup)
        
        # Add commands
        if hasattr(aaz_group, 'commands') and aaz_group.commands:
            for cmd_name, command in aaz_group.commands.items():
                proto_command = convert_aaz_command_to_crs(command)
                proto_group.commands.append(proto_command)
        
        return proto_group

    def create_component_proto(root_group):
        """Create the main component protobuf"""
        proto_component = component_pb2.CrsPluginComponent()
        
        # Set metadata
        proto_component.metadata.name = component_name
        proto_component.metadata.version = "1.0.0"  # Default version
        proto_component.metadata.uri = component_uri
        if root_group.help:
            proto_component.metadata.help.short = root_group.help.short or f"Azure {component_name} CLI commands"
            if root_group.help.lines:
                proto_component.metadata.help.long = "\n".join(root_group.help.lines)
        
        # Set interface
        proto_group = convert_aaz_command_group_to_proto(root_group)
        proto_component.interface.command_group.CopyFrom(proto_group)
        
        return proto_component

    # Find the specific module's command tree
    root_group = specs_manager.find_command_group(module_name)
    if root_group:
        # Create protobuf component
        proto_component = create_component_proto(root_group)
        
        # Create output directory
        os.makedirs(output_path, exist_ok=True)
        
        # Save as binary protobuf file
        binary_file = os.path.join(output_path, f"{module_name}_component.pb")
        with open(binary_file, 'wb') as f:
            f.write(proto_component.SerializeToString())
        
        # Also save as JSON for debugging
        json_file = os.path.join(output_path, f"{module_name}_component.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json_data = MessageToJson(
                proto_component, 
                preserving_proto_field_name=True,
                sort_keys=True,
                indent=2
            )
            f.write(json_data)
        
        # Count commands and groups
        def count_items(group):
            cmd_count = len(group.commands) if hasattr(group, 'commands') else 0
            group_count = len(group.command_groups) if hasattr(group, 'command_groups') else 0
            
            for subgroup in (group.command_groups or {}).values():
                sub_cmd, sub_group = count_items(subgroup)
                cmd_count += sub_cmd
                group_count += sub_group
            
            return cmd_count, group_count
        
        total_commands, total_groups = count_items(root_group)
        
        print(f"✅ Component protobuf saved to: {binary_file}")
        print(f"📄 Component JSON saved to: {json_file}")
        print(f"📊 Found {total_groups} command groups and {total_commands} commands")
        print(f"🔗 Component URI: {component_uri}")
    else:
        print(f"❌ Module '{module_name}' not found in AAZ repository")
     
