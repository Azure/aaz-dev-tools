

class PlaneEnum:
    Mgmt = "mgmt-plane"

    # # data planes should be subdivided by module
    # Data_KeyVault = "data-plane_keyvault"

    _config = {
        Mgmt: {
            "client": "MgmtClient",  # MgmtClient is implemented in azure.cli.core.aaz._client
        },
        # Data_KeyVault: {
        #     "swagger_modules": ("keyvault", ),
        # }
    }

    @classmethod
    def choices(cls):
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))

    @classmethod
    def is_valid_swagger_module(cls, plane, module_name):
        swagger_modules = cls._config[plane].get('swagger_modules', None)
        if not swagger_modules or module_name in swagger_modules:
            return True
        return False

    @classmethod
    def http_client(cls, plane):
        return cls._config[plane]['client']


__all__ = ["PlaneEnum"]
