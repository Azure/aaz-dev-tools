import click
import logging
from flask import Blueprint
import sys

from aaz_dev import protos

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
@click.option(
    "--component-uri",
    required=True,
    help="URI of the component"
)
def export_component(component_name, component_uri, output_path):
    print(f"Exporting component: {component_name} with URI: {component_uri}")
    print(f"Using AAZ path: {Config.AAZ_PATH}")    
    

    import json
    import os
    from aaz_dev.command.controller.specs_manager import AAZSpecsManager
    
    specs_manager = AAZSpecsManager()
    module_name = component_name.lower()
    module_commands = {
        "componentName": component_name,
        "componentUri": component_uri,
        "commands": []
    }
    

    print(f"Looking for commands in module: {module_name}")
    count = 0
    
    for command in specs_manager.iter_commands():
        # Check if the command belongs to the specified module
        # For commands like 'az network vnet create', the module is 'network'
        if len(command.names) >= 2 and command.names[0] == module_name:
            print(f"Found command: {' '.join(command.names)}")
            count += 1
            
            # Sort versions by name and pick the latest
            if not command.versions:
                print(f"Warning: No versions for command {' '.join(command.names)}")
                continue
            latest_version = sorted(command.versions, key=lambda v: v.name, reverse=True)[0]
            
            cfg_reader = specs_manager.load_resource_cfg_reader_by_command_with_version(command, latest_version)
            if not cfg_reader:
                print(f"Warning: Could not load configuration for command {' '.join(command.names)} version {latest_version.name}")
                continue
            
            command_info = {
                "name": " ".join(command.names),
                "version": latest_version.name,
                "resources": [
                    {
                        "plane": res.plane,
                        "id": res.id,
                        "version": res.version
                    } for res in latest_version.resources
                ],
                "configuration": cfg_reader.cfg.to_primitive()
            }
            
            module_commands["commands"].append(command_info)
    
    print(f"Found {count} commands for module {module_name}")
    
    output_file = f"{output_path}/{component_name}.json"
    os.makedirs(output_path, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(module_commands, f, indent=2)
    
    print(f"Component exported to {output_file}")
    
    return module_commands
