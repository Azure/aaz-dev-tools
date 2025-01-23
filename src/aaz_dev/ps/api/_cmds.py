import click
import logging
from flask import Blueprint
import sys
import os
import subprocess

from utils.config import Config

logger = logging.getLogger('backend')

bp = Blueprint('ps-cmds', __name__, url_prefix='/PS/CMDs', cli_group="ps")
bp.cli.short_help = "Manage powershell commands."


@bp.cli.command("generate-powershell", short_help="Generate powershell code based on selected azure cli module.")
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
    help="The local path of azure-cli repo. Only required when generate from azure-cli module."
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_extension_path,
    help="The local path of azure-cli-extension repo. Only required when generate from azure-cli extension."
)
@click.option(
    "--powershell-path", '--ps',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_powershell_path,
    help="The local path of azure-powershell repo."
)
@click.option(
    "--extension-or-module-name", '--name',
    required=True,
    help="Name of the module in azure-cli or the extension in azure-cli-extensions"
)
@click.option(
    "--swagger-path", '-s',
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_PATH,
    required=not Config.SWAGGER_PATH,
    callback=Config.validate_and_setup_swagger_path,
    expose_value=False,
    help="The local path of azure-rest-api-specs repo. Official repo is https://github.com/Azure/azure-rest-api-specs"
)
def generate_powershell(extension_or_module_name, cli_path=None, cli_extension_path=None, powershell_path=None):
    from ps.controller.autorest_configuration_generator import PSAutoRestConfigurationGenerator
    from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
    from ps.templates import get_templates

    # Module path in azure-powershell repo

    powershell_path = os.path.join(powershell_path, "src")
    if not os.path.exists(powershell_path):
        logger.error(f"Path `{powershell_path}` not exist")
        sys.exit(1)

    if cli_path is not None:
        assert Config.CLI_PATH is not None
        manager = AzMainManager()
    else:
        assert cli_extension_path is not None
        assert Config.CLI_EXTENSION_PATH is not None
        manager = AzExtensionManager()

    if not manager.has_module(extension_or_module_name):
        logger.error(f"Cannot find module or extension `{extension_or_module_name}`")
        sys.exit(1)

    # generate README.md for powershell from CLI, ex, for Oracle, README.md should be generated in src/Oracle/Oracle.Autorest/README.md in azure-powershell repo
    ps_generator = PSAutoRestConfigurationGenerator(manager, extension_or_module_name)
    ps_cfg = ps_generator.generate_config()

    autorest_module_path = os.path.join(powershell_path, ps_cfg.module_name, f"{ps_cfg.module_name}.Autorest")
    if not os.path.exists(autorest_module_path):
        os.makedirs(autorest_module_path)
    readme_file = os.path.join(autorest_module_path, "README.md")
    if os.path.exists(readme_file):
        # read until to the "### AutoRest Configuration"
        with open(readme_file, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("### AutoRest Configuration"):
                    lines = lines[:i]
                    break
    else:
        lines = []

    tmpl = get_templates()['autorest']['configuration']
    data = tmpl.render(cfg=ps_cfg)
    lines.append(data)
    with open(readme_file, "w") as f:
        f.writelines(lines)

    print(f"Generated {readme_file}")
    # Generate and build PowerShell module from the README.md file generated above
    print("Start to generate the PowerShell module from the README.md file in " + autorest_module_path)

    # Execute autorest to generate the PowerShell module
    original_cwd = os.getcwd()
    os.chdir(autorest_module_path)
    exit_code = os.system("pwsh -Command autorest")

     # Print the output of the generation
    if (exit_code != 0):
        print("Failed to generate the module")
        os.chdir(original_cwd)
        sys.exit(1)
    else:
        print("Code generation succeeded.")
        # print(result.stdout)

    os.chdir(original_cwd)
    # Execute autorest to generate the PowerShell module
    print("Start to build the generated PowerShell module")
    result = subprocess.run(
        ["pwsh", "-File", 'build-module.ps1'],
        capture_output=True,
        text=True,
        cwd=autorest_module_path
    )

    if (result.returncode != 0):
        print("Failed to build the module, please see following output for details:")
        print(result.stderr)
        sys.exit(1)
    else:
        print("Module build succeeds, and you may run the generated module by executing the following command: `./run-module.ps1` in " + autorest_module_path)
