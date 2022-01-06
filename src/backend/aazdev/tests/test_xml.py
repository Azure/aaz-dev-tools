import tempfile

from aazdev.operations.xml import XMLSerializer
from command.model.configuration import CMDResource, CMDConfiguration
from swagger.controller.command_generator import CommandGenerator
from swagger.tests.common import SwaggerSpecsTestCase
from utils import config


class XMLSerializerTest(SwaggerSpecsTestCase):
    @staticmethod
    def test_virtual_network():
        resource_id = "/subscriptions/{}/resourcegroups/{}/providers/microsoft.network/virtualnetworks/{}"
        cmd_resource = CMDResource({"id": resource_id, "version": "2021-05-01"})
        generator = CommandGenerator(module_name="(MgmtPlane)/network", swagger_path=config.SWAGGER_PATH)
        resources = generator.load_resources([cmd_resource])
        command_group = generator.create_draft_command_group(resources[resource_id])

        model = CMDConfiguration({"resources": [cmd_resource], "command_group": command_group})
        with tempfile.TemporaryFile() as fp:
            xml = XMLSerializer(model).to_xml()
            fp.write(xml)
            fp.seek(0)
            deserialized_model = XMLSerializer(CMDConfiguration).from_xml(fp)
            assert xml == XMLSerializer(deserialized_model).to_xml()

    def test_all_mgmt_modules(self):
        for rp in self.get_mgmt_plane_resource_providers():
            print(f"\n{rp}")
            resource_map = rp.get_resource_map(read_only=True)
            resource_ids = []
            resource_versions = set()
            for r_id, r_version_map in resource_map.items():
                resource_ids.append(r_id)
                resource_versions.update(r_version_map.keys())
            generator = CommandGenerator(module_name=str(rp.swagger_module))
            for r_id in resource_ids:
                for v in resource_versions:
                    if v in resource_map[r_id]:
                        cmd_resource = CMDResource({"id": r_id, "version": str(v)})
                        resources = generator.load_resources([cmd_resource])
                        command_group = generator.create_draft_command_group(resources[r_id])

                        model = CMDConfiguration({"resources": [cmd_resource], "command_group": command_group})
                        with tempfile.TemporaryFile() as fp:
                            xml = XMLSerializer(model).to_xml()
                            fp.write(xml)
                            fp.seek(0)
                            deserialized_model = XMLSerializer(CMDConfiguration).from_xml(fp)
                            assert xml == XMLSerializer(deserialized_model).to_xml()
