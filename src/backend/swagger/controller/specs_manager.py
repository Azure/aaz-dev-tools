from swagger.model.specs import SwaggerSpecs
from utils.constants import PlaneEnum


from utils import Config, exceptions
from collections import OrderedDict


class SwaggerSpecsManager:

    @classmethod
    def get_modules(cls, plane):
        specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
        if plane == PlaneEnum.Mgmt:
            modules = specs.get_mgmt_plane_modules()
        elif plane == PlaneEnum.Data:
            modules = specs.get_data_plane_modules()
        else:
            raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}'")

        result = OrderedDict()
        for m in modules:
            for rp in m.get_resource_providers():
                module = rp.swagger_module
                module_str = str(module)
                if module_str not in result:
                    result[module_str] = module
        return [*result.values()]

    @classmethod
    def get_module(cls, plane, mod_names):
        specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
        if plane == PlaneEnum.Mgmt:
            module = specs.get_mgmt_plane_module(*mod_names.split('/'))
        elif plane == PlaneEnum.Data:
            module = specs.get_data_plane_module(*mod_names.split('/'))
        else:
            raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}-plane'")

        if not module:
            raise exceptions.ResourceNotFind(f"Module not find '{mod_names}'")
        return module

    @classmethod
    def get_resource_providers(cls, plane, mod_names):
        module = cls.get_module(plane, mod_names)

        return [*module.get_resource_providers()]

    @classmethod
    def get_resource_provider(cls, plane, mod_names, rp_name):
        rps = cls.get_resource_providers(plane, mod_names)
        rp = None
        for v in rps:
            if v.name == rp_name:
                rp = v
                break
        if rp is None:
            raise exceptions.ResourceNotFind(f"resource provider not find '{rp_name}'")
        return rp

    @classmethod
    def get_grouped_resource_map(cls, plane, mod_names, rp_name):
        rp = cls.get_resource_provider(plane, mod_names, rp_name)
        resource_map = rp.get_resource_map()
        resource_op_group_map = OrderedDict()
        for resource_id, version_map in resource_map.items():
            op_group_name = cls.get_resource_op_group_name(version_map)
            if op_group_name not in resource_op_group_map:
                resource_op_group_map[op_group_name] = OrderedDict()
            resource_op_group_map[op_group_name][resource_id] = version_map
        return resource_op_group_map

    @classmethod
    def get_resource_op_group_name(cls, version_map):
        _, latest_resource = sorted(
            version_map.items(),
            key=lambda item: str(item[0]),
            reverse=True
        )[0]
        return latest_resource.get_operation_group_name() or ""

    @classmethod
    def get_resource_version_map(cls, plane, mod_names, resource_id, rp_name=None):
        if rp_name:
            rps = [cls.get_resource_provider(plane, mod_names, rp_name)]
        else:
            rps = cls.get_resource_providers(plane, mod_names)

        version_maps = []
        resource_rps = []
        for rp in rps:
            resource_map = rp.get_resource_map()
            if resource_id in resource_map:
                version_maps.append(resource_map[resource_id])
                resource_rps.append(rp)

        if not version_maps:
            raise exceptions.ResourceNotFind(f"Resource not find '{resource_id}'")

        if len(resource_rps) > 1:
            raise exceptions.InvalidAPIUsage(
                "Find multiple resource providers: \n" +
                "\n".join([r.folder_path for r in resource_rps])
            )
        return version_maps[0]

    @classmethod
    def get_resource_in_version(cls, plane, mod_names, resource_id, version, rp_name=None):
        if rp_name:
            rps = [cls.get_resource_provider(plane, mod_names, rp_name)]
        else:
            rps = cls.get_resource_providers(plane, mod_names)

        resources = []
        for rp in rps:
            resource_map = rp.get_resource_map()
            if resource_id in resource_map and version in resource_map[resource_id]:
                resources.append(resource_map[resource_id][version])

        if not resources:
            raise exceptions.ResourceNotFind(f"Resource not find '{resource_id}' '{version}'")

        if len(resources) > 1:
            raise exceptions.InvalidAPIUsage(
                "Find multiple resources in files: \n" +
                "\n".join([r.file_path for r in resources])
            )

        return resources[0]
