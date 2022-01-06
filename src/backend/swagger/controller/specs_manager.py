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
    def get_resource_providers(cls, plane, mod_names):
        specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
        if plane == PlaneEnum.Mgmt:
            module = specs.get_mgmt_plane_module(*mod_names.split('/'))
        elif plane == PlaneEnum.Data:
            module = specs.get_data_plane_module(*mod_names.split('/'))
        else:
            raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}-plane'")

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
            _, latest_resource = sorted(
                version_map.items(),
                key=lambda item: str(item[0]),
                reverse=True
            )[0]
            op_group_name = latest_resource.get_operation_group_name() or ""
            if op_group_name not in resource_op_group_map:
                resource_op_group_map[op_group_name] = OrderedDict()
            resource_op_group_map[op_group_name][resource_id] = version_map
        return rp, resource_op_group_map
