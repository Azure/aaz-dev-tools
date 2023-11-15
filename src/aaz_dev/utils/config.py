import os
from packaging import version
from .plane import PlaneEnum


class Config:

    MIN_CLI_CORE_VERSION = version.parse("2.54.0")

    AAZ_PATH = os.environ.get("AAZ_PATH", None)
    SWAGGER_PATH = os.environ.get("AAZ_SWAGGER_PATH", None)
    SWAGGER_MODULE_PATH = os.environ.get("AAZ_SWAGGER_MODULE_PATH", None)

    DEFAULT_PLANE = PlaneEnum.Mgmt
    DEFAULT_SWAGGER_MODULE = os.environ.get("AAZ_SWAGGER_MODULE", None)  # use '/' to join sub modules
    DEFAULT_RESOURCE_PROVIDER = os.environ.get("AAZ_SWAGGER_RESOURCE_PROVIDER", None)

    CLI_PATH = os.environ.get("AAZ_CLI_PATH", None)
    CLI_EXTENSION_PATH = os.environ.get("AAZ_CLI_EXTENSION_PATH", None)

    AAZ_DEV_FOLDER = os.path.expanduser(
        os.environ.get("AAZ_DEV_FOLDER", os.path.join("~", ".aaz_dev"))
    )
    AAZ_DEV_WORKSPACE_FOLDER = os.path.expanduser(
        os.environ.get("AAZ_DEV_WORKSPACE_FOLDER", os.path.join(AAZ_DEV_FOLDER, "workspaces"))
    )

    # Flask configurations
    HOST = os.environ.get("AAZ_HOST", '127.0.0.1')
    PORT = int(os.environ.get("AAZ_PORT", 5000))
    STATIC_FOLDER = '../ui'
    STATIC_URL_PATH = '/'

    CLI_DEFAULT_PROFILE = 'latest'

    CLI_PROFILES = [
        CLI_DEFAULT_PROFILE,
        "2020-09-01-hybrid",
        "2019-03-01-hybrid",
        "2018-03-01-hybrid",
        "2017-03-09-profile",
    ]

    @classmethod
    def validate_and_setup_host(cls, ctx, param, value):
        cls.HOST = value
        return cls.HOST

    @classmethod
    def validate_and_setup_port(cls, ctx, param, value):
        cls.PORT = value
        return cls.PORT

    @classmethod
    def validate_and_setup_aaz_path(cls, ctx, param, value):
        # TODO: verify folder structure
        if value != cls.AAZ_PATH:
            cls.AAZ_PATH = os.path.expanduser(value)
            if not os.path.exists(cls.AAZ_PATH):
                raise ValueError(f"Path '{cls.AAZ_PATH}' does not exist.")
        return cls.AAZ_PATH

    @classmethod
    def validate_and_setup_swagger_path(cls, ctx, param, value):
        # TODO: verify folder structure
        if value != cls.SWAGGER_PATH:
            cls.SWAGGER_PATH = os.path.expanduser(value)
            if not os.path.exists(cls.SWAGGER_PATH):
                raise ValueError(f"Path '{cls.SWAGGER_PATH}' does not exist.")
        return cls.SWAGGER_PATH

    @classmethod
    def validate_and_setup_swagger_module_path(cls, ctx, param, value):
        # TODO: verify folder structure
        if value != cls.SWAGGER_MODULE_PATH:
            cls.SWAGGER_MODULE_PATH = os.path.expanduser(value)
            if not os.path.exists(cls.SWAGGER_MODULE_PATH):
                raise ValueError(f"Path '{cls.SWAGGER_MODULE_PATH}' does not exist.")
        return cls.SWAGGER_MODULE_PATH

    @classmethod
    def validate_and_setup_default_swagger_module(cls, ctx, param, value):
        cls.DEFAULT_SWAGGER_MODULE = value
        return cls.DEFAULT_SWAGGER_MODULE

    @classmethod
    def validate_and_setup_default_resource_provider(cls, ctx, param, value):
        cls.DEFAULT_RESOURCE_PROVIDER = value
        return cls.DEFAULT_RESOURCE_PROVIDER

    @classmethod
    def validate_and_setup_cli_path(cls, ctx, param, value):
        # TODO: verify folder structure
        if value != cls.CLI_PATH:
            cls.CLI_PATH = os.path.expanduser(value)
            if not os.path.exists(cls.CLI_PATH):
                raise ValueError(f"Path '{cls.CLI_PATH}' does not exist.")
        return cls.CLI_PATH

    @classmethod
    def validate_and_setup_cli_extension_path(cls, ctx, param, value):
        # TODO: verify folder structure
        if value != cls.CLI_EXTENSION_PATH:
            cls.CLI_EXTENSION_PATH = os.path.expanduser(value)
            if not os.path.exists(cls.CLI_EXTENSION_PATH):
                raise ValueError(f"Path '{cls.CLI_EXTENSION_PATH}' does not exist.")
        return cls.CLI_EXTENSION_PATH

    @classmethod
    def validate_and_setup_aaz_dev_workspace_folder(cls, ctx, param, value):
        # TODO: verify folder
        if value != cls.AAZ_DEV_WORKSPACE_FOLDER:
            cls.AAZ_DEV_WORKSPACE_FOLDER = os.path.expanduser(value)
            if os.path.exists(cls.AAZ_DEV_WORKSPACE_FOLDER) and not os.path.isdir(cls.AAZ_DEV_WORKSPACE_FOLDER):
                raise ValueError(f"Path '{cls.AAZ_DEV_WORKSPACE_FOLDER}' is not a folder.")
        return cls.AAZ_DEV_WORKSPACE_FOLDER


__all__ = ["Config"]
