from aazdev.tests.common import ApiTestCase


class SwaggerSpecsApiTestCase(ApiTestCase):

    def test_index(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Docs/Index')
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(isinstance(data, list))
            search_pages = [*data]
            idx = 0
            while idx < len(search_pages):
                page = search_pages[idx]
                self.assertTrue('id' in page and 'title' in page)
                if 'file' in page:
                    rv = c.get(f'/Docs/Index/{page["id"]}')
                    self.assertTrue(rv.status_code == 200)
                    content = rv.get_data()
                    self.assertTrue(rv.mimetype == "text/markdown")
                    rv = c.get(f'/Docs/{page["file"]}')
                    self.assertTrue(rv.status_code == 302)
                    self.assertTrue(rv.location.endswith(f"?#/Documents/{page['id']}"))
                else:
                    self.assertTrue('pages' in page)
                    search_pages.extend(page['pages'])
                idx += 1
