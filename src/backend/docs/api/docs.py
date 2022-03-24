from flask import Blueprint, jsonify, make_response, redirect, url_for
from ..controller.docs_manager import DocsManager
from utils import exceptions


bp = Blueprint('docs', __name__, url_prefix='/Docs')


@bp.route("/Index", methods=("GET",))
def get_all_documents():
    manager = DocsManager()
    pages = manager.pages
    return jsonify(pages)


@bp.route("/Index/<doc_id>", methods=("GET", ))
def get_document(doc_id):
    manager = DocsManager()
    page = manager.get_page(doc_id)
    if not page:
        raise exceptions.ResourceNotFind(f"Page not find: '{doc_id}'")
    content, mimetype = manager.load_page_content(page)
    if content is not None:
        resp = make_response(content)
        resp.mimetype = mimetype
        return resp
    else:
        return "", 204


@bp.route("/<path:file_path>", methods=("GET",))
def get_document_content(file_path):
    manager = DocsManager()
    page = manager.find_page_by_file(file_path)
    if not page:
        raise exceptions.ResourceNotFind(f"Page not find: '{file_path}'")
    return redirect(f"/?#/Documents/{page['id']}")
