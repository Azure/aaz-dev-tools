from flask import Blueprint, jsonify
import flask
import glob
import os

bp = Blueprint('docs', __name__, url_prefix='/Documentation')
    

@bp.route("/all", methods=("GET",))
def get_all_documents():
    docs_path = os.path.abspath(os.path.join(os.path.join(os.path.join(os.path.join(flask.current_app.root_path, os.pardir), os.pardir), os.pardir), 'docs'))
    files_and_folders = glob.glob(docs_path+'/**', recursive=True)
    res = []
    for file_or_folder in files_and_folders:
        if file_or_folder.endswith('.md'):
            res.append(file_or_folder.replace("\\", '/').replace(docs_path.replace('\\','/'), '.'))
    return jsonify(res)

