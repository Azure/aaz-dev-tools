from command.model.configuration import CMDClientConfig


class ClientCfgReader:

    def __init__(self, cfg):
        assert isinstance(cfg, CMDClientConfig)
        self.cfg = cfg

    def find_arg_by_var(self, arg_var):
        if not self.cfg.arg_group:
            return None
        for arg in self.cfg.arg_group.args:
            if arg.var == arg_var:
                return arg
        return None
