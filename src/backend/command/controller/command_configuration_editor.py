from command.model.configuration import CMDResource, CMDConfiguration


class CommandConfigurationEditor:

    def __init__(self, workspace):
        self.workspace = workspace

    def _load_cmd_config(self, config_path):
        # load command configuration from persistence layer
        return None

    def _fetch_config_path_by_resource_id(self, resource_id, v):
        # TODO: read from repo index
        return None

    def _fetch_config_path_by_cmd_name(self, cmd_name, v):
        # TODO: read from repo index
        return None

    def add_resource_by_cmd(self, cmd_name, v):
        config_path = self._fetch_config_path_by_cmd_name(cmd_name, v)
        cmd_config = self._load_cmd_config(config_path)
        # TODO:

    def add_resource_by_swagger(self, module, resource_id, v, inherent_v=None):
        # config_path = self._fetch_config_path_by_resource_id(resource_id, v)
        resources = [
            CMDResource({
                "id": resource_id,
                "version": v
            })
        ]
        if inherent_v:
            config_path = self._fetch_config_path_by_resource_id(resource_id, inherent_v)
            assert config_path is not None, "config not exist error"
            inherent_config = self._load_cmd_config(config_path)    # type: CMDConfiguration
            resources = inherent_config.resources   # use inherent configuration resources





