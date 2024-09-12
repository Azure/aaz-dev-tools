from flask import Blueprint, jsonify, request, url_for

from utils.config import Config
from utils import exceptions
from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
from cli.controller.portal_cli_generator import PortalCliGenerator
from cli.model.view import CLIModule
from command.controller.specs_manager import AAZSpecsManager
import logging

logging.basicConfig(level="INFO")

bp = Blueprint('ps', __name__, url_prefix='/CLI/PS')

