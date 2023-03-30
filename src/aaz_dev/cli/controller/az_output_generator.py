from command.model.configuration._output import CMDObjectOutput, CMDArrayOutput, CMDStringOutput


class AzOutputGenerator:

    def __init__(self, output, cmd_ctx):
        self._output = output
        self._cmd_ctx = cmd_ctx

    @property
    def ref(self):
        if isinstance(self._output, (CMDObjectOutput, CMDArrayOutput, CMDStringOutput)) and self._output.ref:
            ref, is_selector = self._cmd_ctx.get_variant(self._output.ref)
            if is_selector:
                return f'{ref}.required()'
            else:
                return ref
        return None

    @property
    def next_link(self):
        if isinstance(self._output, (CMDArrayOutput, )) and self._output.next_link:
            next_link, is_selector = self._cmd_ctx.get_variant(self._output.next_link)
            assert not is_selector
            return next_link
        return None

    @property
    def client_flatten(self):
        if isinstance(self._output, (CMDObjectOutput, CMDArrayOutput)):
            return self._output.client_flatten is True
        elif isinstance(self._output, CMDStringOutput):
            return False
        else:
            raise NotImplementedError()

    @property
    def value(self):
        if isinstance(self._output, CMDStringOutput):
            return self._output.value
        else:
            raise NotImplementedError()
