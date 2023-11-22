from command.model.configuration import CMDJsonSubresourceSelector, CMDArrayIndexBase, CMDObjectIndexBase, \
    CMDObjectIndexDiscriminator, CMDObjectIndexAdditionalProperties, CMDObjectIndex, CMDArrayIndex, CMDSchema, \
    CMDObjectIndexAdditionalProperties, CMDSelectorIndex, CMDSimpleIndexBase, CMDSimpleIndex
from utils.case import to_camel_case


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

    def iter_scopes_for_get(self):
        for scope in self._iter_scopes():
            yield scope

    def iter_scopes_for_set(self):
        for scope in self._iter_scopes(is_set=True):
            yield scope

    def _iter_scopes(self, is_set=False):
        scope_name = 'result'
        scope_define = self.variant_key
        for scope in _iter_selector_scopes_by_index_base(self._json, scope_name, scope_define, [], None, self._cmd_ctx, is_set):
            yield scope


def _iter_selector_scopes_by_index(index, scope_name, scope_define, idx_lines, cmd_ctx, is_set):
    assert isinstance(index, (CMDObjectIndex, CMDArrayIndex, CMDSimpleIndex))
    if scope_define is not None:
        yield scope_name, scope_define, idx_lines, None, None, False
    scope_define = f"{scope_name}.{index.name}"
    for scope in _iter_selector_scopes_by_index_base(index, scope_name, scope_define, [], None, cmd_ctx, is_set):
        yield scope


def _iter_selector_scopes_by_index_base(index, scope_name, scope_define, idx_lines, previous_identifiers, cmd_ctx, is_set):

    def _handle_idx_lines_for_end():
        if previous_identifiers and is_set:
            for identifier in previous_identifiers:
                assert isinstance(identifier, CMDSchema)
                assert identifier.arg
                if identifier.name == "[Index]" or identifier.name.startswith('[]'):
                    assert idx_lines == ["idx = next(filters)[0]"]
                    assert scope_define == f"{scope_name}[idx]"
                    idx_lines[0] = f"idx = next(filters, [len({scope_name})])[0]"
                    if identifier.name == "[Index]":
                        arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                        assert not hide
                        idx_lines.append(f"{arg_keys} = idx")
                    return
                elif identifier.name == "{Key}":
                    assert idx_lines == ["idx = next(filters)[0]"]
                    assert scope_define == f"{scope_name}[idx]"
                    arg_keys, hide = cmd_ctx.get_argument(identifier.arg)
                    assert not hide
                    idx_lines[0] = f"idx = next(filters, [{arg_keys}.to_serialized_data()])[0]"
                    return

    if isinstance(index, CMDSimpleIndexBase):
        is_end = True
        _handle_idx_lines_for_end()
        yield scope_name, scope_define, idx_lines, None, None, is_end
    elif isinstance(index, CMDObjectIndexBase):
        is_end = False
        if index.prop:
            assert isinstance(index.prop, CMDSelectorIndex)
            yield scope_name, scope_define, idx_lines, None, None, is_end
            for scope in _iter_selector_scopes_by_index(index.prop, scope_name, None, [], cmd_ctx, is_set):
                yield scope
        elif index.discriminator:
            yield scope_name, scope_define, idx_lines, None, None, is_end
            next_scope_define = f"[{scope_name}]"
            for scope in _iter_selector_scopes_by_index_base(
                    index.discriminator, scope_name, next_scope_define, [], None, cmd_ctx, is_set):
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
                    if identifier.name == '{Key}':
                        filter_key = "[0]"
                        filter_value = arg_keys
                        filter_is_constant = False
                    else:
                        assert identifier.name.startswith('{}')
                        filter_key = f"[1]{identifier.name[2:]}"
                        filter_value = arg_keys
                        filter_is_constant = False
                    filters.append((filter_key, filter_value, filter_is_constant))

                yield scope_name, scope_define, idx_lines, filter_builder, filters, is_end
                next_idx_lines = [
                    "idx = next(filters)[0]"
                ]
                next_scope_define = f"{scope_name}[idx]"
                for scope in _iter_selector_scopes_by_index_base(
                        index.additional_props.item, scope_name, next_scope_define, next_idx_lines,
                        index.additional_props.identifiers, cmd_ctx, is_set):
                    yield scope

            else:
                assert not index.additional_props.identifiers
                is_end = True
                _handle_idx_lines_for_end()
                yield scope_name, scope_define, idx_lines, None, None, is_end
        else:
            is_end = True
            _handle_idx_lines_for_end()
            yield scope_name, scope_define, idx_lines, None, None, is_end
    elif isinstance(index, CMDObjectIndexDiscriminator):
        is_end = False
        assert scope_define == f"[{scope_name}]"
        filter_builder = f"enumerate({scope_name})"
        filter_key = f"[1].{index.property}"
        filter_value = index.value
        filter_is_constant = True
        filters = [(filter_key, filter_value, filter_is_constant)]
        if index.prop:
            yield scope_name, scope_define, idx_lines, filter_builder, filters, is_end
            next_idx_lines = [
                "idx = next(filters)[0]"
            ]
            next_scope_define = f"{scope_name}[idx]"
            for scope in _iter_selector_scopes_by_index(index.prop, scope_name, next_scope_define, next_idx_lines, cmd_ctx, is_set):
                yield scope
        elif index.discriminator:
            yield scope_name, scope_define, idx_lines, filter_builder, filters, is_end
            next_scope_define = f"[{scope_name}]"
            for scope in _iter_selector_scopes_by_index_base(
                    index.discriminator, scope_name, next_scope_define, [], None, cmd_ctx, is_set):
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

            yield scope_name, scope_define, idx_lines, filter_builder, filters, is_end

            next_idx_lines = [
                "idx = next(filters)[0]"
            ]
            next_scope_define = f"{scope_name}[idx]"
            for scope in _iter_selector_scopes_by_index_base(index.item, scope_name, next_scope_define, next_idx_lines, index.identifiers, cmd_ctx, is_set):
                yield scope
        else:
            assert not index.identifiers
            is_end = True
            _handle_idx_lines_for_end()
            yield scope_name, scope_define, idx_lines, None, None, is_end
