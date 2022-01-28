from tempfile import TemporaryFile

from command.model.configuration import CMDConfiguration, XMLSerializer
from swagger.controller.command_generator import CommandGenerator
from swagger.controller.specs_manager import SwaggerSpecsManager
from swagger.tests.common import SwaggerSpecsTestCase
from swagger.utils import exceptions
from utils.plane import PlaneEnum

MUTE_ERROR_MESSAGES = (
    "type is not supported",
    "format is not supported"
)


class XMLSerializerTest(SwaggerSpecsTestCase):

    def test_virtual_network_e2e(self):
        resource_id = "/subscriptions/{}/resourcegroups/{}/providers/microsoft.network/virtualnetworks/{}"

        generator = CommandGenerator()
        specs_manager = SwaggerSpecsManager()
        resource = specs_manager.get_resource_in_version(
            plane=PlaneEnum.Mgmt, mod_names="network", resource_id=resource_id, version="2021-05-01")

        generator.load_resources([resource])
        command_group = generator.create_draft_command_group(resource)

        model = CMDConfiguration({"resources": [resource.to_cmd()], "commandGroups": [command_group]})
        with TemporaryFile("w+t", encoding="utf-8") as fp:
            xml = XMLSerializer(model).to_xml()
            fp.write(xml)
            fp.seek(0)
            deserialized_model = XMLSerializer(CMDConfiguration).from_xml(fp.read())
            assert xml == XMLSerializer(deserialized_model).to_xml()

    def test_all_mgmt_modules_coverage(self):
        total = count = 0
        for rp in self.get_mgmt_plane_resource_providers():
            resource_map = rp.get_resource_map()
            generator = CommandGenerator()

            for r_id, r_version_map in resource_map.items():
                for v, resource in r_version_map.items():
                    try:
                        generator.load_resources([resource])
                        command_group = generator.create_draft_command_group(resource)
                    except exceptions.InvalidSwaggerValueError as err:
                        if err.msg not in MUTE_ERROR_MESSAGES:
                            print(err)
                    except Exception:
                        print(resource_map[r_id][v])
                    else:
                        total += 1
                        try:
                            model = CMDConfiguration({"resources": [resource.to_cmd()], "commandGroups": [command_group]})
                            with TemporaryFile("w+t", encoding="utf-8") as fp:
                                xml = XMLSerializer(model).to_xml()
                                fp.write(xml)
                                fp.seek(0)
                                deserialized_model = XMLSerializer(CMDConfiguration).from_xml(fp.read())
                        except Exception:
                            print(f"--module {rp.swagger_module.name} --resource-id {r_id} --version {v}")
                        else:
                            if xml == XMLSerializer(deserialized_model).to_xml():
                                count += 1
                            else:
                                print(f"--module {rp.swagger_module.name} --resource-id {r_id} --version {v}")

        coverage = count / total
        print(f"\nCoverage: {count} / {total} = {coverage:.2%}")
