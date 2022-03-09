from command.model.configuration._output import CMDObjectOutput, CMDArrayOutput, CMDStringOutput


class AzOutputGenerator:

    def __init__(self, output, cmd_ctx):
        self._output = output
        self._cmd_ctx = cmd_ctx

    @property
    def ref(self):
        if isinstance(self._output, (CMDObjectOutput, CMDArrayOutput)) and self._output.ref:
            return self._cmd_ctx.get_variant(self._output.ref)
        return None

    @property
    def client_flatten(self):
        if isinstance(self._output, (CMDObjectOutput, CMDArrayOutput)):
            return self._output.client_flatten is True
        else:
            raise NotImplementedError()

    @property
    def value(self):
        if isinstance(self._output, CMDStringOutput):
            return self._output.value
        else:
            raise NotImplementedError()
