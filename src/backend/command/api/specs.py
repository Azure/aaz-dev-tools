from flask import Blueprint, jsonify, request, url_for
from utils import exceptions

bp = Blueprint('specs', __name__, url_prefix='/AAZ/Specs')

