from command.model.configuration import CMDJsonSubresourceSelector, CMDArrayIndexBase, CMDObjectIndexBase, \
    CMDObjectIndexDiscriminator, CMDObjectIndexAdditionalProperties, CMDObjectIndex, CMDArrayIndex, CMDSchema
from utils.case import to_camel_case, to_snack_case



class AzJsonSelectorGenerator:

    def __init__(self, cmd_ctx, selector):
        assert isinstance(selector, CMDJsonSubresourceSelector)
        self._cmd_ctx = cmd_ctx
        self._selector = selector
        self._cmd_ctx.set_selector(selector)
        self.name = self._cmd_ctx.get_variant(selector.var, name_only=True)
        self.variant_key, is_selector_variant = cmd_ctx.get_variant(selector.ref)
        assert not is_selector_variant

        self._json = self._selector.json

    @property
    def cls_name(self):
        return f'{to_camel_case(self.name)}Selector'

    def iter_scopes(self, is_set=False):
        filters = None

        yield filters,
        index = self._json


def _iter_selector_scopes_by_index(index, cmd_ctx):
    if isinstance(index, CMDObjectIndex):
        # index.name
        key = f'result.{index.name}'

        filter_builder = None
        filters = []
        if index.additional_props:
            if index.additional_props.identifiers:
                filter_builder = 'result.items()'
                for identifier in index.additional_props.identifiers:
                    assert isinstance(identifier, CMDSchema)
                    assert identifier.arg
                    arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                    assert not hide
                    if identifier.name == '{Key}':
                        filter_lambda = f'lambda e: e[0] == {arg_keys}'
                    else:
                        assert identifier.name.startswith('{}')
                        filter_lambda = f'lambda e: e[1]{identifier.name[2:]} == {arg_keys}'
                    filters.append(filter_lambda)
                if index.additional_props.item:
                    pass
                else:
                    # end of index
                    pass
        elif index.discriminator:
            pass
        elif index.prop:
            pass
        else:
            # end of index
            pass
    elif isinstance(index, CMDArrayIndex):
        key = f'result.{index.name}'

        filter_builder = None
        filters = []
        if index.identifiers:
            filter_builder = 'enumerate(result)'
            for identifier in index.identifiers:
                assert isinstance(identifier, CMDSchema)
                assert identifier.arg
                arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                assert not hide
                if identifier.name == '[Index]':
                    filter_lambda = f'lambda e: e[0] == {arg_keys}'
                else:
                    assert identifier.name.startswith('[]')
                    filter_lambda = f'lambda e: e[1]{identifier.name[2:]} == {arg_keys}'
                filters.append(filter_lambda)

            if index.item:
                pass
            else:
                # end of index
                pass


def _iter_selector_scopes_by_index_base(index, key,  cmd_ctx):
    if isinstance(index, CMDObjectIndexBase):

        pass
    elif isinstance(index, CMDObjectIndexDiscriminator):
        pass
    elif isinstance(index, CMDArrayIndexBase):
        assign_line = f'result = {key}'

        pass

