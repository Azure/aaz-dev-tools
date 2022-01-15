from flask import Blueprint, jsonify, request, url_for
from command.controller.config_editor import ConfigEditorWorkspaceManager
from command.model.editor import CMDEditorWorkspace
from utils import exceptions
import os

bp = Blueprint('specs', __name__, url_prefix='/AAZ/Specs')

