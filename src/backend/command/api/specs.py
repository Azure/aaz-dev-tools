from flask import Blueprint, jsonify, request, url_for
from utils import exceptions

bp = Blueprint('specs', __name__, url_prefix='/AAZ/Specs')


# modules
@bp.route("/CommandTree/Nodes/<names_path:node_names>", methods=("GET",))
def command_tree_node(node_names):

    pass


@bp.route("/CommandTree/Nodes/<names_path:node_names>/Leaves/<name:leaf_name>", methods=("GET",))
def command_tree_leaf(node_names, leaf_name):

    pass
