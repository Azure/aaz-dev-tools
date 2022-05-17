from collections import OrderedDict

from swagger.model.specs import SwaggerSpecs, ResourceProvider
from utils import exceptions
from utils.config import Config
from utils.plane import PlaneEnum


class SwaggerSpecsManager:

    def __init__(self):
        self.specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
        self._modules_cache = {}
        self._rps_cache = {}
        self._resource_op_group_map_cache = {}
        self._resource_map_cache = {}

    def get_resource_map(self, rp):
        assert isinstance(rp, ResourceProvider)
        key = str(rp)
        if key not in self._resource_map_cache:
            self._resource_map_cache[key] = rp.get_resource_map()
        return self._resource_map_cache[key]

    def get_modules(self, plane):
        if plane in self._modules_cache:
            return self._modules_cache[plane]

        if plane == PlaneEnum.Mgmt:
            modules = self.specs.get_mgmt_plane_modules(plane=plane)
        elif plane in PlaneEnum.choices():
            modules = self.specs.get_data_plane_modules(plane=plane)
        else:
            raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}'")

        result = OrderedDict()
        for m in modules:
            for rp in m.get_resource_providers():
                module = rp.swagger_module
                module_str = str(module)
                if module_str not in result:
                    result[module_str] = module

        self._modules_cache[plane] = [*result.values()]
        return self._modules_cache[plane]

    def get_module(self, plane, mod_names):
        if isinstance(mod_names, str):
            mod_names = mod_names.split('/')

        if plane == PlaneEnum.Mgmt:
            module = self.specs.get_mgmt_plane_module(*mod_names, plane=plane)
        elif plane in PlaneEnum.choices():
            module = self.specs.get_data_plane_module(*mod_names, plane=plane)
        else:
            raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}'")

        if not module:
            raise exceptions.ResourceNotFind(f"Module not find '{mod_names}'")
        return module

    def get_resource_providers(self, plane, mod_names):
        if isinstance(mod_names, str):
            mod_names = mod_names.split('/')

        key = (plane, tuple(mod_names))
        if key not in self._rps_cache:
            module = self.get_module(plane, mod_names)
            self._rps_cache[key] = module.get_resource_providers()
        return self._rps_cache[key]

    def get_resource_provider(self, plane, mod_names, rp_name):
        if isinstance(mod_names, str):
            mod_names = mod_names.split('/')

        rps = self.get_resource_providers(plane, mod_names)
        rp = None
        for v in rps:
            if v.name == rp_name:
                rp = v
                break
        if rp is None:
            raise exceptions.ResourceNotFind(f"resource provider not find '{rp_name}'")
        return rp

    def get_grouped_resource_map(self, plane, mod_names, rp_name):
        if isinstance(mod_names, str):
            mod_names = mod_names.split('/')

        key = (plane, tuple(mod_names), rp_name)
        if key in self._resource_op_group_map_cache:
            return self._resource_op_group_map_cache[key]

        rp = self.get_resource_provider(plane, mod_names, rp_name)
        resource_map = self.get_resource_map(rp)
        resource_op_group_map = OrderedDict()
        for resource_id, version_map in resource_map.items():
            op_group_name = self.get_resource_op_group_name(version_map)
            if op_group_name not in resource_op_group_map:
                resource_op_group_map[op_group_name] = OrderedDict()
            resource_op_group_map[op_group_name][resource_id] = version_map
        self._resource_op_group_map_cache[key] = resource_op_group_map
        return self._resource_op_group_map_cache[key]

    def get_resource_op_group_name(self, version_map):
        _, latest_resource = sorted(
            version_map.items(),
            key=lambda item: str(item[0]),
            reverse=True
        )[0]
        return latest_resource.get_operation_group_name() or ""

    def get_resource_version_map(self, plane, mod_names, resource_id, rp_name=None):
        if isinstance(mod_names, str):
            mod_names = mod_names.split('/')

        if rp_name:
            rps = [self.get_resource_provider(plane, mod_names, rp_name)]
        else:
            rps = self.get_resource_providers(plane, mod_names)

        version_maps = []
        resource_rps = []
        for rp in rps:
            resource_map = self.get_resource_map(rp)
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

    def get_resource_in_version(self, plane, mod_names, resource_id, version, rp_name=None):
        if isinstance(mod_names, str):
            mod_names = mod_names.split('/')

        if rp_name:
            rps = [self.get_resource_provider(plane, mod_names, rp_name)]
        else:
            rps = self.get_resource_providers(plane, mod_names)

        resources = []
        for rp in rps:
            resource_map = self.get_resource_map(rp)
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
