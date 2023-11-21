from collections import OrderedDict

from swagger.model.specs import SwaggerSpecs, SingleModuleSwaggerSpecs, ResourceProvider, SwaggerModule
from utils import exceptions
from utils.config import Config
from utils.plane import PlaneEnum


class SwaggerSpecsModuleManager:

    def __init__(self, plane, module):
        self.plane = plane
        self.module = module
        self._rps_catch = None
        self._resource_op_group_map_cache = {}
        self._resource_map_cache = {}
        assert plane == PlaneEnum.Mgmt or PlaneEnum.is_data_plane(plane), f"Invalid plane: '{self.plane}'"
        assert isinstance(module, SwaggerModule), f"Invalid module type: '{type(module)}'"

    def get_resource_providers(self):
        if self._rps_catch is None:
            self._rps_catch = self.module.get_resource_providers()
        return self._rps_catch

    def get_resource_provider(self, rp_name):
        rps = self.get_resource_providers()
        rp = None
        for v in rps:
            if v.name == rp_name:
                rp = v
                break
        if rp is None:

            raise exceptions.ResourceNotFind(f"resource provider not find '{rp_name}'")
        return rp

    def get_grouped_resource_map(self, rp_name):
        key = rp_name
        if key in self._resource_op_group_map_cache:
            return self._resource_op_group_map_cache[key]

        rp = self.get_resource_provider(rp_name)
        resource_map = self.get_resource_map(rp)
        resource_op_group_map = OrderedDict()
        for resource_id, version_map in resource_map.items():
            op_group_name = self.get_resource_op_group_name(version_map)
            if op_group_name not in resource_op_group_map:
                resource_op_group_map[op_group_name] = OrderedDict()
            resource_op_group_map[op_group_name][resource_id] = version_map
        self._resource_op_group_map_cache[key] = resource_op_group_map
        return self._resource_op_group_map_cache[key]

    @staticmethod
    def get_resource_op_group_name(version_map):
        _, latest_resource = sorted(
            version_map.items(),
            key=lambda item: str(item[0]),
            reverse=True
        )[0]
        return latest_resource.get_operation_group_name() or ""

    def get_resource_version_map(self, resource_id, rp_name=None):
        if rp_name:
            rps = [self.get_resource_provider(rp_name)]
        else:
            rps = self.get_resource_providers()

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

    def get_resource_in_version(self, resource_id, version, rp_name=None):
        if rp_name:
            rps = [self.get_resource_provider(rp_name)]
        else:
            rps = self.get_resource_providers()

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

    def get_resource_map(self, rp):
        assert isinstance(rp, ResourceProvider)
        key = str(rp)
        if key not in self._resource_map_cache:
            self._resource_map_cache[key] = rp.get_resource_map()
        return self._resource_map_cache[key]


class SwaggerSpecsManager:

    def __init__(self):
        if Config.SWAGGER_PATH:
            self.specs = SwaggerSpecs(folder_path=Config.SWAGGER_PATH)
        elif Config.SWAGGER_MODULE_PATH:
            if not Config.DEFAULT_SWAGGER_MODULE:
                raise ValueError("SWAGGER_MODULE is required when using SWAGGER_MODULE_PATH")
            self.specs = SingleModuleSwaggerSpecs(
                folder_path=Config.SWAGGER_MODULE_PATH, module_name=Config.DEFAULT_SWAGGER_MODULE)
        else:
            raise ValueError("Require SWAGGER_PATH or SWAGGER_MODULE_PATH")

        self._modules_cache = {}
        self._module_managers_cache = {}

    def get_modules(self, plane):
        if plane in self._modules_cache:
            return self._modules_cache[plane]

        if plane == PlaneEnum.Mgmt:
            modules = self.specs.get_mgmt_plane_modules(plane=plane)
        elif PlaneEnum.is_data_plane(plane):
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
        elif PlaneEnum.is_data_plane(plane):
            module = self.specs.get_data_plane_module(*mod_names, plane=plane)
        else:
            raise exceptions.InvalidAPIUsage(f"invalid plane name '{plane}'")

        if not module:
            raise exceptions.ResourceNotFind(f"Module not find '{'/'.join(mod_names)}'")
        return module

    def get_module_manager(self, plane, mod_names, without_catch=False) -> SwaggerSpecsModuleManager:
        key = (plane, tuple(mod_names))
        if without_catch or key not in self._module_managers_cache:
            module = self.get_module(plane, mod_names)
            self._module_managers_cache[key] = SwaggerSpecsModuleManager(plane, module)

        return self._module_managers_cache[key]

    def get_swagger_resource(self, plane, mod_names, resource_id, version):
        return self.get_module_manager(
            plane=plane, mod_names=mod_names
        ).get_resource_in_version(resource_id, version)
