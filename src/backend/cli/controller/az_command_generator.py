from cli.model.atomic import CLIAtomicCommand
from utils.case import to_camel_case


class AzCommandGenerator:

    def __init__(self, cmd: CLIAtomicCommand):
        self.cmd = cmd

    @property
    def name(self):
        return ' '.join(self.cmd.names)

    @property
    def cls_name(self):
        return to_camel_case(self.cmd.names[-1])

    @property
    def help(self):
        return self.cmd.help

    @property
    def register_info(self):
        return self.cmd.register_info
