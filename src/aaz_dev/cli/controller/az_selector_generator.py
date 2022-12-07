from command.model.configuration import CMDJsonSubresourceSelector, CMDArrayIndexBase, CMDObjectIndexBase, \
    CMDObjectIndexDiscriminator, CMDObjectIndexAdditionalProperties, CMDObjectIndex, CMDArrayIndex, CMDSchema, \
    CMDObjectIndexAdditionalProperties, CMDSelectorIndex
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

    def iter_scopes(self):
        scope_name = 'result'
        scope_define = self.variant_key
        # yield scope, scope_define, None, None, False
        for scope in _iter_selector_scopes_by_index_base(self._json, scope_name, scope_define, None, self._cmd_ctx):
            yield scope


def _iter_selector_scopes_by_index(index, scope_name, scope_define, cmd_ctx):
    assert isinstance(index, (CMDObjectIndex, CMDArrayIndex))
    if scope_define is not None:
        yield scope_name, scope_define, None, None, False
    scope_define = f"{scope_name}.{index.name}"
    for scope in _iter_selector_scopes_by_index_base(index, scope_name, scope_define, None, cmd_ctx):
        yield scope


def _iter_selector_scopes_by_index_base(index, scope_name, scope_define, previous_identifiers, cmd_ctx):
    if isinstance(index, CMDObjectIndexBase):
        is_end = False
        if index.prop:
            assert isinstance(index.prop, CMDSelectorIndex)
            yield scope_name, scope_define, None, None, is_end
            for scope in _iter_selector_scopes_by_index(index.prop, scope_name, None, cmd_ctx):
                yield scope
        elif index.discriminator:
            yield scope_name, scope_define, None, None, is_end
            next_scope_define = f"[{scope_name}]"
            for scope in _iter_selector_scopes_by_index_base(
                    index.discriminator, scope_name, next_scope_define, None, cmd_ctx):
                yield scope
        elif index.additional_props:
            assert isinstance(index.additional_props, CMDObjectIndexAdditionalProperties)
            if index.additional_props.item:
                assert index.additional_props.identifiers
                filter_builder = f"{scope_name}.items()"
                filters = []
                for identifier in index.additional_props.identifiers:
                    assert isinstance(identifier, CMDSchema)
                    assert identifier.arg
                    arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                    assert not hide
                    if identifier.name == '[Key]':
                        filter_key = "[0]"
                        filter_value = arg_keys
                        filter_is_constant = False
                    else:
                        assert identifier.name.startswith('[]')
                        filter_key = f"[1]{identifier.name[2:]}"
                        filter_value = arg_keys
                        filter_is_constant = False
                    filters.append((filter_key, filter_value, filter_is_constant))

                yield scope_name, scope_define, filter_builder, filters, is_end

                next_scope_define = f"{scope_name}[next(filters)[0]]"
                for scope in _iter_selector_scopes_by_index_base(
                        index.additional_props.item, scope_name, next_scope_define,
                        index.additional_props.identifiers, cmd_ctx):
                    yield scope

            else:
                assert not index.additional_props.identifiers
                is_end = True
                if previous_identifiers:
                    for identifier in previous_identifiers:
                        assert isinstance(identifier, CMDSchema)
                        assert identifier.arg
                        if identifier.name == "[Index]":
                            assert scope_define == f"{scope_name}[next(filters)[0]]"
                            scope_define = f"{scope_name}[next(filters, [len({scope_name})])[0]]"
                            break
                        elif identifier.name == "[Key]":
                            assert scope_define == f"{scope_name}[next(filters)[0]]"
                            arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                            assert not hide
                            scope_define = f"{scope_name}[next(filters, [{arg_keys}.to_serialized_data()])[0]]"
                            break
                yield scope_name, scope_define, None, None, is_end
        else:
            is_end = True
            if previous_identifiers:
                for identifier in previous_identifiers:
                    assert isinstance(identifier, CMDSchema)
                    assert identifier.arg
                    if identifier.name == "[Index]":
                        assert scope_define == f"{scope_name}[next(filters)[0]]"
                        scope_define = f"{scope_name}[next(filters, [len({scope_name})])[0]]"
                        break
                    elif identifier.name == "[Key]":
                        assert scope_define == f"{scope_name}[next(filters)[0]]"
                        arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                        assert not hide
                        scope_define = f"{scope_name}[next(filters, [{arg_keys}.to_serialized_data()])[0]]"
                        break
            yield scope_name, scope_define, None, None, is_end
    elif isinstance(index, CMDObjectIndexDiscriminator):
        is_end = False
        assert scope_define == f"[{scope_name}]"
        filter_builder = f"enumerate({scope_name})"
        filter_key = f"[1].{index.property}"
        filter_value = index.value
        filter_is_constant = True
        filters = [(filter_key, filter_value, filter_is_constant)]
        if index.prop:
            yield scope_name, scope_define, filter_builder, filters, is_end
            next_scope_define = f"{scope_name}[next(filters)[0]]"
            for scope in _iter_selector_scopes_by_index(index.prop, scope_name, next_scope_define, cmd_ctx):
                yield scope
        elif index.discriminator:
            yield scope_name, scope_define, filter_builder, filters, is_end
            next_scope_define = f"[{scope_name}]"
            for scope in _iter_selector_scopes_by_index_base(
                    index.discriminator, scope_name, next_scope_define, None, cmd_ctx):
                yield scope
        else:
            # Not support to end in a discriminator
            raise NotImplementedError()
    elif isinstance(index, CMDArrayIndexBase):
        is_end = False
        if index.item:
            assert index.identifiers
            filter_builder = f"enumerate({scope_name})"
            filters = []
            for identifier in index.identifiers:
                assert isinstance(identifier, CMDSchema)
                assert identifier.arg
                arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                assert not hide
                if identifier.name == '[Index]':
                    filter_key = "[0]"
                    filter_value = arg_keys
                    filter_is_constant = False
                else:
                    assert identifier.name.startswith('[]')
                    filter_key = f"[1]{identifier.name[2:]}"
                    filter_value = arg_keys
                    filter_is_constant = False
                filters.append((filter_key, filter_value, filter_is_constant))

            yield scope_name, scope_define, filter_builder, filters, is_end

            next_scope_define = f"{scope_name}[next(filters)[0]]"
            for scope in _iter_selector_scopes_by_index_base(index.item, scope_name, next_scope_define, index.identifiers, cmd_ctx):
                yield scope
        else:
            assert not index.identifiers
            is_end = True
            if previous_identifiers:
                for identifier in previous_identifiers:
                    assert isinstance(identifier, CMDSchema)
                    assert identifier.arg
                    if identifier.name == "[Index]":
                        assert scope_define == f"{scope_name}[next(filters)[0]]"
                        scope_define = f"{scope_name}[next(filters, [len({scope_name})])[0]]"
                        break
                    elif identifier.name == "[Key]":
                        assert scope_define == f"{scope_name}[next(filters)[0]]"
                        arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                        assert not hide
                        scope_define = f"{scope_name}[next(filters, [{arg_keys}.to_serialized_data()])[0]]"
                        break
            yield scope_name, scope_define, None, None, is_end
