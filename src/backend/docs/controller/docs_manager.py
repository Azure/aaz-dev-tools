import os
import mimetypes
import yaml
from utils import exceptions
from flask import send_file


class DocsManager:

    docs_folder = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(os.path.abspath(__file__))
                        )))), 'Docs')

    @classmethod
    def _iter_over_page(cls, pages):
        for page in pages:
            yield page
            if 'pages' in page:
                for sub_page in cls._iter_over_page(page['pages']):
                    yield sub_page

    def __init__(self):
        self.pages = self.load_index()
        self._page_map = {}
        for page in self._iter_over_page(self.pages):
            self._page_map[page['id']] = page

    def load_index(self):
        path = os.path.join(self.docs_folder, 'index.yaml')
        if not os.path.exists(path) or not os.path.isfile(path):
            raise exceptions.ResourceNotFind(f"Index file not exist at: '{path}'")
        with open(path, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        if 'nav' not in data or not isinstance(data['nav'], list):
            raise exceptions.ResourceConflict("Invalid index file: nav miss or is not a list")
        pages = []
        for idx, item in enumerate(data['nav']):
            pages.append(self._convert_page(item, str(idx)))
        return pages

    def _convert_page(self, item, *keys):
        page = {}
        title, content = [*item.items()][0]
        page['title'] = title.strip()
        page['id'] = '-'.join([str(key) for key in keys])
        if not page['id'] and not page['title']:
            raise exceptions.ResourceConflict(f"Invalid index file: Page idx or title is invalid")
        if isinstance(content, str):
            doc_path = os.path.join(self.docs_folder, content)
            if not os.path.exists(doc_path) or not os.path.isfile(doc_path):
                raise exceptions.ResourceNotFind(f"Invalid index file: Page file not exist at: '{doc_path}'")
            page['file'] = content
        elif isinstance(content, list):
            page['pages'] = []
            for idx, sub_item in enumerate(content):
                page['pages'].append(self._convert_page(sub_item, *keys, idx))
        else:
            raise exceptions.ResourceConflict(f"Invalid index file: invalid data: {content}")
        return page

    def get_page(self, doc_id):
        return self._page_map.get(doc_id, None)

    def load_page_content(self, page):
        if 'file' not in page:
            return None
        doc_path = os.path.join(self.docs_folder, page['file'])
        return send_file(
            doc_path,
            mimetype="text/markdown"
        )

    def find_page_by_file(self, file):
        for doc_id, page in self._page_map.items():
            if 'file' in page and file == page['file']:
                return page
        return None

    def load_material(self, file):
        m_path = os.path.join(self.docs_folder, file)
        if not os.path.exists(m_path) or not os.path.isfile(m_path):
            return None
        else:
            return send_file(
                m_path,
                mimetype=mimetypes.guess_type(m_path)[0]
            )
