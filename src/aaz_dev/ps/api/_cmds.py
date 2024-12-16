import click
import logging
from flask import Blueprint
import sys

from utils.config import Config

logger = logging.getLogger('backend')

bp = Blueprint('ps-cmds', __name__, url_prefix='/PS/CMDs', cli_group="ps")
bp.cli.short_help = "Manage powershell commands."
