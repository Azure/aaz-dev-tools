import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from cli.api import _cmds
from cli.controller.az_module_manager import AzModuleManager
from swagger.model.specs import SwaggerSpecs, TypeSpecResourceProvider
from utils.config import Config
from utils.plane import PlaneEnum


class CodegenRegressionTest(TestCase):
    def test_generate_rejects_incomplete_selections_before_updating_cli(self):
        resources = {"/test": {"v1": object()}}
        good = SimpleNamespace(name="Good", default_tag="v1", get_resource_map_by_tag=lambda _: resources)
        missing = SimpleNamespace(name="Missing", default_tag=None)
        typespec = TypeSpecResourceProvider("Test", [], None)
        reader = SimpleNamespace(iter_commands=lambda: iter([
            (["test", "show"], SimpleNamespace(version="v1")),
        ]))
        empty_reader = SimpleNamespace(iter_commands=lambda: iter([]))

        cases = [
            ("no providers", [], reader, False),
            ("typespec only", [typespec], reader, False),
            ("missing tag", [missing], reader, False),
            ("partial selection", [good, missing], reader, False),
            ("missing models", [good], None, False),
            ("no commands", [good], empty_reader, False),
            ("valid selection", [good], reader, True),
        ]
        with TemporaryDirectory() as folder:
            (Path(folder) / "specification" / "test").mkdir(parents=True)
            for name, providers, cfg_reader, valid in cases:
                with self.subTest(name=name):
                    module_manager = SimpleNamespace(
                        get_resource_providers=lambda: providers,
                        get_openapi_resource_provider=lambda name: next(r for r in providers if r.name == name),
                    )
                    discovery = SimpleNamespace(get_module_manager=lambda *args: module_manager)
                    with patch.object(Config, "SWAGGER_PATH", folder), \
                            patch.object(Config, "CLI_EXTENSION_PATH", folder), \
                            patch.object(_cmds, "SwaggerSpecsManager", return_value=discovery), \
                            patch.object(_cmds, "WorkspaceManager") as workspaces, \
                            patch.object(_cmds, "AAZSpecsManager") as aaz, \
                            patch.object(_cmds, "AzExtensionManager") as extensions:
                        workspaces.new.return_value.is_in_memory = True
                        workspaces.new.return_value.iter_command_tree_nodes.return_value = []
                        workspaces.new.return_value.iter_command_tree_leaves.return_value = []
                        aaz.return_value.load_resource_cfg_reader.return_value = cfg_reader
                        manager = extensions.return_value
                        manager.has_module.return_value = True
                        manager.load_module.return_value = SimpleNamespace(profiles={})
                        if valid:
                            inspect.unwrap(_cmds.generate.callback)("test", "test")
                            manager.update_module.assert_called_once()
                            profile = manager.update_module.call_args.args[1]["latest"]
                            self.assertEqual(profile.command_groups["test"].commands["show"].version, "v1")
                        else:
                            with self.assertRaises(SystemExit) as error:
                                inspect.unwrap(_cmds.generate.callback)("test", "test")
                            self.assertEqual(error.exception.code, 1)
                            manager.update_module.assert_not_called()
                            manager.create_new_mod.assert_not_called()
                            if name in ("no providers", "typespec only", "missing tag", "partial selection"):
                                workspaces.new.assert_not_called()

    def test_submodules_preserve_typespec_and_openapi_layouts(self):
        for plane, segment in ((PlaneEnum.Mgmt, "resource-manager"), (PlaneEnum._Data, "data-plane")):
            with self.subTest(plane=plane), TemporaryDirectory() as folder:
                root = Path(folder) / "specification" / "test"
                entry = root / "Service.TypeSpec"
                entry.mkdir(parents=True)
                (entry / "main.tsp").write_text(
                    ("@armProviderNamespace\n" if plane == PlaneEnum.Mgmt else "") +
                    "namespace Test.Service;\n", encoding="utf-8",
                )
                (entry / "tspconfig.yaml").write_text("{}\n", encoding="utf-8")
                specs = SwaggerSpecs(folder)
                get_module = specs.get_mgmt_plane_module if plane == PlaneEnum.Mgmt else specs.get_data_plane_module
                with patch.object(Config, "SWAGGER_PATH", folder):
                    self.assertEqual(Path(get_module("test", plane=plane).folder_path), root)
                    module = get_module("test", entry.name, plane=plane)
                    self.assertIsNotNone(module)
                    self.assertEqual(Path(module.folder_path), entry)
                    providers = module.get_resource_providers()
                    self.assertEqual([r.name for r in providers], ["Test.Service"])
                    self.assertEqual(len(providers[0].entry_files), 1)

                    (root / segment / entry.name).mkdir(parents=True)
                    module = get_module("test", entry.name, plane=plane)
                    self.assertEqual(Path(module.folder_path), entry)
                    self.assertEqual([r.name for r in module.get_resource_providers()], ["Test.Service"])

                    nested = root / segment / "group" / "nested"
                    (nested / "Test.Provider" / "stable").mkdir(parents=True)
                    (root / "group").mkdir()
                    module = get_module("test", "group", "nested", plane=plane)
                    self.assertEqual(Path(module.folder_path), nested)
                    self.assertEqual(module.names, ["test", "group", "nested"])
                    self.assertEqual([r.name for r in module.get_resource_providers()], ["Test.Provider"])
                    self.assertIsNone(get_module("test", "missing", plane=plane))

    def test_patch_checks_called_loaders_not_import_text(self):
        plain = "class Loader:\n    def load_command_table(self, args):\n        return {}\n"
        helper = (
            "    def _load(self, args):\n"
            "        from azure.cli.core.aaz import {loader}\n"
            "        {loader}(self, 'test.aaz', args)\n"
        )
        cases = [
            ("plain", plain, True),
            ("comment", plain + "    # from azure.cli.core.aaz import load_aaz_command_table\n", True),
            ("unused import", "from azure.cli.core.aaz import load_aaz_command_table\n" + plain, True),
            ("unused helper", plain + helper.format(loader="load_aaz_command_table"), True),
            ("nested unused helper", plain.replace(
                "        return {}",
                "        def unused():\n"
                "            from azure.cli.core.aaz import load_aaz_command_table\n"
                "            load_aaz_command_table(self, 'test.aaz', args)\n"
                "        return {}",
            ), True),
        ]
        for loader in ("load_aaz_command_table", "load_aaz_command_table_args_guided"):
            cases.append((loader, plain.replace("return {}", "return self._load(args)") +
                          helper.format(loader=loader), False))
            cases.append((loader + " alias",
                          "from azure.cli.core.aaz import " + loader + " as load_commands\n" +
                          plain.replace("return {}", "return load_commands(self, 'test.aaz', args)"), False))
        cases.append(("helper cycle", plain.replace("return {}", "return self._load(args)") +
                      "    def _load(self, args):\n        return self.load_command_table(args)\n", True))
        with TemporaryDirectory() as folder:
            init = Path(folder) / "__init__.py"
            manager = AzModuleManager()
            manager.get_aaz_path = lambda _: str(Path(folder) / "aaz")
            for name, source, needs_patch in cases:
                with self.subTest(name=name):
                    init.write_text(source, encoding="utf-8")
                    patches = list(manager._patch_module("test"))
                    self.assertEqual(len(patches), int(needs_patch))
                    if patches:
                        compile(patches[0][1], str(init), "exec")
                        init.write_text(patches[0][1], encoding="utf-8")
                        self.assertEqual(list(manager._patch_module("test")), [])
