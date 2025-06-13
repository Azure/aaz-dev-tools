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
    "--component-name", '--name',
    required=True,
    help="Name of the component"
)
@click.option(
    "--component-uri",
    required=True,
    help="URI of the component"
)
def export_component(component_name, component_uri):
    print(Config.AAZ_PATH)
    print(component_name, component_uri)
    
    pass
