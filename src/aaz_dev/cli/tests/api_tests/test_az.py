from cli.tests.common import CommandTestCase
from utils.config import Config
from utils.base64 import b64encode_str
from utils.stage import AAZStageEnum
from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
import os
import shutil


class APIAzTest(CommandTestCase):

    def test_list_profiles(self):
        with self.app.test_client() as c:
            rv = c.get(f"/CLI/Az/Profiles")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(data == Config.CLI_PROFILES)

    def test_list_main_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f"/CLI/Az/Main/Modules")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data))
            self.assertTrue('name' in data[0])
            self.assertTrue('folder' in data[0])
            self.assertTrue('url' in data[0])
            for mod in data:
                rv = c.get(mod['url'])
                self.assertTrue(rv.status_code == 200)

    def test_list_extension_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f"/CLI/Az/Extension/Modules")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertTrue(len(data))
            self.assertTrue('name' in data[0])
            self.assertTrue('folder' in data[0])
            self.assertTrue('url' in data[0])
            for mod in data:
                rv = c.get(mod['url'])
                self.assertTrue(rv.status_code == 200, mod['url'])

    def test_create_new_module_in_main(self):
        mod_name = "aaz-new-module"
        manager = AzMainManager()
        path = manager.get_mod_path(mod_name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        try:
            with self.app.test_client() as c:
                rv = c.post(f"/CLI/Az/Main/Modules", json={
                    "name": mod_name
                })
                self.assertTrue(rv.status_code == 200)
                data = rv.get_json()
                self.assertTrue(data['name'] == mod_name)
                self.assertTrue(data['folder'] == path)
                for profile_name in Config.CLI_PROFILES:
                    self.assertTrue(profile_name in data['profiles'])
                    self.assertTrue(data['profiles'][profile_name] == {'name': profile_name})
        finally:
            shutil.rmtree(path, ignore_errors=True)

    def test_create_new_module_in_extension(self):
        mod_name = "aaz-new-extension"
        manager = AzExtensionManager()
        path = manager.get_mod_path(mod_name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        try:
            with self.app.test_client() as c:
                rv = c.post(f"/CLI/Az/Extension/Modules", json={
                    "name": mod_name
                })
                self.assertTrue(rv.status_code == 200)
                data = rv.get_json()
                self.assertTrue(data['name'] == mod_name)
                self.assertTrue(data['folder'] == path)
                for profile_name in Config.CLI_PROFILES:
                    self.assertTrue(profile_name in data['profiles'])
                    self.assertTrue(data['profiles'][profile_name] == {'name': profile_name})
        finally:
            shutil.rmtree(path, ignore_errors=True)

    def test_generate_edge_order_in_main_repo(self):
        self.prepare_aaz()
        mod_name = "aaz-edge-order"
        manager = AzMainManager()
        path = manager.get_mod_path(mod_name)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        with self.app.test_client() as c:
            rv = c.post(f"/CLI/Az/Main/Modules", json={
                "name": mod_name
            })
            self.assertTrue(rv.status_code == 200)
            profiles = rv.get_json()['profiles']

            # latest profile
            version = '2021-12-01'
            profile = profiles[Config.CLI_DEFAULT_PROFILE]
            profile['commandGroups'] = {
                'edge-order': {
                    'names': ['edge-order'],
                    'commandGroups': {
                        'address': {
                            'names': ['edge-order', 'address'],
                            'commands': {
                                'create': {
                                    'names': ['edge-order', 'address', 'create'],
                                    'registered': True,
                                    'version': version,
                                },
                                'delete': {
                                    'names': ['edge-order', 'address', 'delete'],
                                    'registered': True,
                                    'version': version,
                                },
                                'list': {
                                    'names': ['edge-order', 'address', 'list'],
                                    'registered': True,
                                    'version': version,
                                },
                                'show': {
                                    'names': ['edge-order', 'address', 'show'],
                                    'registered': True,
                                    'version': version,
                                },
                                'update': {
                                    'names': ['edge-order', 'address', 'update'],
                                    'registered': True,
                                    'version': version,
                                }
                            }
                        },
                        'order': {
                            'names': ['edge-order', 'order'],
                            'commands': {
                                'list': {
                                    'names': ['edge-order', 'order', 'list'],
                                    'version': version,
                                },
                                'show': {
                                    'names': ['edge-order', 'order', 'show'],
                                    'version': version,
                                },
                            }
                        },
                        'order-item': {
                            'names': ['edge-order', 'order-item'],
                            'commands': {
                                'cancel': {
                                    'names': ['edge-order', 'order-item', 'cancel'],
                                    'registered': True,
                                    'version': version,
                                },
                                'create': {
                                    'names': ['edge-order', 'order-item', 'create'],
                                    'registered': True,
                                    'version': version,
                                },
                                'delete': {
                                    'names': ['edge-order', 'order-item', 'delete'],
                                    'registered': True,
                                    'version': version,
                                },
                                'show': {
                                    'names': ['edge-order', 'order-item', 'show'],
                                    'registered': True,
                                    'version': version,
                                },
                                'update': {
                                    'names': ['edge-order', 'order-item', 'update'],
                                    'registered': True,
                                    'version': version,
                                },
                                'return': {
                                    'names': ['edge-order', 'order-item', 'return'],
                                    'registered': True,
                                    'version': version,
                                },
                            }
                        }
                    }
                }
            }

            # 2020-09-01-hybrid profile
            version = '2020-12-01-preview'
            profile = profiles[Config.CLI_PROFILES[1]]
            profile['commandGroups'] = {
                'edge-order': {
                    'names': ['edge-order'],
                    'commandGroups': {
                        'address': {
                            'names': ['edge-order', 'address'],
                            'commands': {
                                'create': {
                                    'names': ['edge-order', 'address', 'create'],
                                    'registered': True,
                                    'version': version,
                                },
                                'delete': {
                                    'names': ['edge-order', 'address', 'delete'],
                                    'registered': True,
                                    'version': version,
                                },
                                'list': {
                                    'names': ['edge-order', 'address', 'list'],
                                    'registered': True,
                                    'version': version,
                                },
                                'show': {
                                    'names': ['edge-order', 'address', 'show'],
                                    'registered': True,
                                    'version': version,
                                },
                                'update': {
                                    'names': ['edge-order', 'address', 'update'],
                                    'registered': True,
                                    'version': version,
                                }
                            }
                        },
                        'order': {
                            'names': ['edge-order', 'order'],
                            'commands': {
                                'list': {
                                    'names': ['edge-order', 'order', 'list'],
                                    'version': version,
                                },
                                'show': {
                                    'names': ['edge-order', 'order', 'show'],
                                    'version': version,
                                },
                            }
                        },
                        'order-item': {
                            'names': ['edge-order', 'order-item'],
                            'commands': {
                                'cancel': {
                                    'names': ['edge-order', 'order-item', 'cancel'],
                                    'registered': True,
                                    'version': version,
                                },
                                'create': {
                                    'names': ['edge-order', 'order-item', 'create'],
                                    'registered': True,
                                    'version': version,
                                },
                                'delete': {
                                    'names': ['edge-order', 'order-item', 'delete'],
                                    'registered': True,
                                    'version': version,
                                },
                                'show': {
                                    'names': ['edge-order', 'order-item', 'show'],
                                    'registered': True,
                                    'version': version,
                                },
                                'update': {
                                    'names': ['edge-order', 'order-item', 'update'],
                                    'registered': True,
                                    'version': version,
                                },
                                'return': {
                                    'names': ['edge-order', 'order-item', 'return'],
                                    'registered': True,
                                    'version': version,
                                },
                            }
                        }
                    }
                }
            }

            rv = c.put(f"/CLI/Az/Main/Modules/{mod_name}", json={
                "profiles": profiles
            })
            self.assertTrue(rv.status_code == 200)

            rv = c.get(f"/CLI/Az/Main/Modules/{mod_name}")
            self.assertTrue(rv.status_code == 200)
            data = rv.get_json()
            self.assertEqual(data['profiles'], profiles)
