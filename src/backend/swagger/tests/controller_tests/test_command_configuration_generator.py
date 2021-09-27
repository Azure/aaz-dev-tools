from swagger.tests.common import SwaggerSpecsTestCase
from swagger.controller.command_configuration_generator import CommandConfigurationGenerator
from swagger.utils import exceptions


class SchemaTest(SwaggerSpecsTestCase):

    def test_monitor_control_service(self):
        rp = next(self.get_mgmt_plane_resource_providers(
                module_filter=lambda m: m.name == "monitor",
                resource_provider_filter=lambda r: r.name == "Microsoft.Insights"
        ))

        generator = CommandConfigurationGenerator()

        version = "2021-04-01"
        resource_map = rp.get_resource_map()
        resource_op_group_map = rp.get_resource_op_group_map(resource_map)
        for op_group_name in [
            "DataCollectionEndpoint", "DataCollectionEndpoints",
            "DataCollectionRule", "DataCollectionRules",
            "DataCollectionRuleAssociation", "DataCollectionRuleAssociations"
        ]:
            resources = []
            for resource_id in resource_op_group_map[op_group_name]:
                resources.append(resource_map[resource_id][version])
            generator.load_resources(resources)

    def test_mgmt_modules(self):
        for rp in self.get_mgmt_plane_resource_providers():
            print(str(rp))
            generator = CommandConfigurationGenerator()
            resource_map = rp.get_resource_map()
            resource_op_group_map = rp.get_resource_op_group_map(resource_map)
            for op_group_name in resource_op_group_map:
                versions = set()
                for resource_id in resource_op_group_map[op_group_name]:
                    versions.update(resource_map[resource_id].keys())
                for version in versions:
                    resources = []
                    for resource_id in resource_op_group_map[op_group_name]:
                        if version in resource_map[resource_id]:
                            resources.append(resource_map[resource_id][version])
                    try:
                        generator.load_resources(resources)
                    except exceptions.InvalidSwaggerValueError as err:
                        print(err)
                    except Exception:
                        print([str(resource) for resource in resources])
                        raise

    def test_data_plane_modules(self):
        for rp in self.get_data_plane_resource_providers():
            print(str(rp))
            generator = CommandConfigurationGenerator()
            resource_map = rp.get_resource_map()
            resource_op_group_map = rp.get_resource_op_group_map(resource_map)
            for op_group_name in resource_op_group_map:
                versions = set()
                for resource_id in resource_op_group_map[op_group_name]:
                    versions.update(resource_map[resource_id].keys())
                for version in versions:
                    resources = []
                    for resource_id in resource_op_group_map[op_group_name]:
                        if version in resource_map[resource_id]:
                            resources.append(resource_map[resource_id][version])
                    try:
                        generator.load_resources(resources)
                    except exceptions.InvalidSwaggerValueError as err:
                        print(err)
                    except Exception:
                        print([str(resource) for resource in resources])
                        raise
