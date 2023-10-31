

def create_data_plane_name(resource_provider):
    return 'data-plane:' + resource_provider.lower()


class PlaneEnum:
    Mgmt = "mgmt-plane"
    _Data = "data-plane"

    @staticmethod
    def Data(resource_provider):
        """For data plane, it's required to provide resource_provider which defined the scope of data plane."""
        return create_data_plane_name(resource_provider)

    _config = {
        Mgmt: {
            "displayName": "Control plane",
            "client": "MgmtClient",  # MgmtClient is implemented in azure.cli.core.aaz._client
        },
        # the general data-plane configuration
        _Data: {
            "displayName": "Data plane",
            # DataPlaneClient is `NOT` implemented, the client configuration with endpoints and scopes is required.
            "client": "DataPlaneClient",
        },
        # example for special data plane configuration
        # create_data_plane_name("Microsoft.Insights"): {
        #     "displayName": "Data plane for Microsoft.Insights",
        #     "client": "InsightDataPlaneClient",
        #     "swagger_modules": ["monitor"],
        # }
    }

    @classmethod
    def is_valid_swagger_module(cls, plane, module_name):
        swagger_modules = cls._config.get(plane, {}).get('swagger_modules', None)
        if not swagger_modules or module_name in swagger_modules:
            return True
        return False
    
    @classmethod
    def is_data_plane(cls, plane):
        return plane.split(":")[0] == cls._Data
    
    @classmethod
    def get_data_plane_scope(cls, plane):
        if not cls.is_data_plane(plane) or plane == cls._Data:
            return None
        return plane.replace(cls._Data + ':', '') or None

    @classmethod
    def http_client(cls, plane):
        if plane in cls._config:
            return cls._config[plane]['client']
        elif cls.is_data_plane(plane):
            # use the default data plane client
            return cls._config[cls._Data]['client']
        else:
            raise ValueError(f"Invalid plane name '{plane}'")


__all__ = ["PlaneEnum"]
