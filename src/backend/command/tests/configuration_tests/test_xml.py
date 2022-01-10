import tempfile

from command.model.configuration import CMDResource, CMDConfiguration, XMLSerializer
from swagger.controller.command_generator import CommandGenerator
from swagger.tests.common import SwaggerSpecsTestCase
from swagger.utils import exceptions
from utils.constants import PlaneEnum

MUTE_ERROR_MESSAGES = (
    "type is not supported",
    "format is not supported"
)


class XMLSerializerTest(SwaggerSpecsTestCase):
    @staticmethod
    def test_virtual_network_e2e():
        resource_id = "/subscriptions/{}/resourcegroups/{}/providers/microsoft.network/virtualnetworks/{}"
        cmd_resource = CMDResource({"id": resource_id, "version": "2021-05-01"})
        generator = CommandGenerator(module_name=f"{PlaneEnum.Mgmt}/network")
        resources = generator.load_resources([cmd_resource])
        command_group = generator.create_draft_command_group(resources[resource_id])

        model = CMDConfiguration({"resources": [cmd_resource], "command_group": command_group})
        with tempfile.TemporaryFile() as fp:
            xml = XMLSerializer(model).to_xml()
            fp.write(xml)
            fp.seek(0)
            deserialized_model = XMLSerializer(CMDConfiguration).from_xml(fp)
            assert xml == XMLSerializer(deserialized_model).to_xml()

    def test_all_mgmt_modules_coverage(self):
        total = count = 0
        for rp in self.get_mgmt_plane_resource_providers(
            module_filter=lambda m: m.name == "network",
            resource_provider_filter=lambda r: r.name == "Microsoft.Network"
        ):
            resource_map = rp.get_resource_map()
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
                        try:
                            resources = generator.load_resources([cmd_resource])
                            command_group = generator.create_draft_command_group(resources[r_id])
                        except exceptions.InvalidSwaggerValueError as err:
                            if err.msg not in MUTE_ERROR_MESSAGES:
                                print(err)
                        except Exception:
                            print(resource_map[r_id][v])
                            raise
                        else:
                            total += 1
                            try:
                                model = CMDConfiguration({"resources": [cmd_resource], "command_group": command_group})
                                with tempfile.TemporaryFile() as fp:
                                    xml = XMLSerializer(model).to_xml()
                                    fp.write(xml)
                                    fp.seek(0)
                                    deserialized_model = XMLSerializer(CMDConfiguration).from_xml(fp)
                            except Exception:
                                print(f"--module {rp.swagger_module.name} --resource-id {r_id} --version {v}")
                            else:
                                if xml == XMLSerializer(deserialized_model).to_xml():
                                    count += 1
                                else:
                                    print(f"--module {rp.swagger_module.name} --resource-id {r_id} --version {v}")
        coverage = count / total
        print(f"\nCoverage: {count} / {total} = {coverage:.2%}")
