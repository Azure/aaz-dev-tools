from .cfg_reader import CfgReader


class CfgValidator:

    def __init__(self, cfg_reader):
        assert isinstance(cfg_reader, CfgReader)
        self.cfg_reader = cfg_reader

    def verify(self):
        # TODO:
        return True

    def _verify_command(self):
        pass

    def _verify_command_arguments(self):
        pass

    def _verify_command_operations(self):
        pass

    def _verify_command_outputs(self):
        pass
