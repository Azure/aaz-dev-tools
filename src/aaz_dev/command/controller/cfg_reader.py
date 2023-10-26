import json

from command.model.configuration import CMDConfiguration, CMDHttpOperation, CMDInstanceUpdateOperation, \
    CMDCommandGroup, CMDArgGroup, CMDObjectArgBase, CMDArrayArgBase, CMDRequestJson, \
    CMDResponseJson, CMDObjectSchemaBase, CMDArraySchemaBase, CMDSchema, CMDHttpRequestJsonBody, \
    CMDJsonInstanceUpdateAction, CMDHttpResponseJsonBody, CMDObjectSchemaDiscriminator, CMDInstanceCreateOperation, \
    CMDJsonInstanceCreateAction, CMDSchemaBase, CMDArraySchema, CMDObjectSchema, CMDInstanceDeleteOperation
from swagger.utils.tools import swagger_resource_path_to_resource_id


class _SchemaIdxEnum:
    Http = "_http"
    Instance = "_instance"
    Request = "_request"
    Response = "_response"
    Create = "_create"
    Update = "_update"
    Path = "_path"
    Query = "_query"
    Header = "_header"
    Body = "_body"
    Json = "_json"


class CfgReader:

    def __init__(self, cfg):
        assert isinstance(cfg, CMDConfiguration)
        self.cfg = cfg
        self.link()

    def link(self):
        self.cfg.link()

    @property
    def resources(self):
        return self.cfg.resources

    def get_used_http_methods(self, resource_id, subresource=None):
        methods = set()
        for _, command in self.iter_commands_by_resource(resource_id, subresource=subresource):
            for operation in command.operations:
                if not isinstance(operation, CMDHttpOperation):
                    continue
                http = operation.http
                if swagger_resource_path_to_resource_id(http.path) != resource_id:
                    continue
                methods.add(http.request.method.lower())
        return tuple(methods) or None

    def get_update_cmd(self, resource_id, subresource=None):
        for cmd_names, command in self.iter_commands_by_resource(resource_id, subresource=subresource):
            for operation in command.operations:
                if isinstance(operation, CMDInstanceUpdateOperation):
                    return cmd_names, command, "GenericOnly"
                if not isinstance(operation, CMDHttpOperation):
                    continue
                http = operation.http
                if swagger_resource_path_to_resource_id(http.path) != resource_id:
                    continue
                if http.request.method.lower() == "patch":
                    return cmd_names, command, "PatchOnly"
        return None

    def iter_cfg_files_data(self):
        main_resource = self.cfg.resources[0]
        data = json.dumps(self.cfg.to_primitive(), ensure_ascii=False)
        yield main_resource.id, data
        for resource in self.cfg.resources[1:]:
            assert resource.version == main_resource.version
            data = json.dumps({"$ref": main_resource.id}, ensure_ascii=False)
            yield resource.id, data

    def iter_commands(self, filter=None):
        groups = []
        for group in self.cfg.command_groups:
            groups.append((group.name.split(" "), group))
        idx = 0
        while idx < len(groups):
            node_names, command_group = groups[idx]
            assert isinstance(command_group, CMDCommandGroup)
            if command_group.commands:
                for command in command_group.commands:
                    cmd_names = [*node_names, command.name]
                    if filter is None or filter(cmd_names, command):
                        yield cmd_names, command
            if command_group.command_groups:
                for group in command_group.command_groups:
                    groups.append(([*node_names, *group.name.split(" ")], group))
            idx += 1

    def iter_commands_by_resource(self, resource_id, subresource=None, version=None):
        """ If sub resource is None, will not iter sub commands.
        """
        def _filter_by_resource(cmd_name, command):
            for r in command.resources:
                if r.id == resource_id and r.subresource == subresource and (not version or r.version == version):
                    return True
            return False
        for result in self.iter_commands(filter=_filter_by_resource):
            yield result

    def iter_commands_by_operations(self, *methods):
        # use 'instance-*' as the methods of instance update operation
        methods = {m.lower() for m in methods}

        def _filter_by_operation(cmd_names, command):
            ops_methods = set()
            has_extra_methods = False
            for operation in command.operations:
                if isinstance(operation, CMDInstanceUpdateOperation):
                    if 'instance-update' not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add('instance-update')
                elif isinstance(operation, CMDInstanceCreateOperation):
                    if 'instance-create' not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add('instance-create')
                elif isinstance(operation, CMDInstanceDeleteOperation):
                    if 'instance-delete' not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add('instance-delete')
                elif isinstance(operation, CMDHttpOperation):
                    http = operation.http
                    if http.request.method.lower() not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add(http.request.method.lower())
            return not has_extra_methods and ops_methods == methods

        for result in self.iter_commands(filter=_filter_by_operation):
            yield result

    def iter_command_group_names(self, parent=None):
        parent_name_len = len(parent.name.split(" ")) if parent else 0
        parent = parent or self.cfg
        if not parent.command_groups:
            return
        for sub_group in parent.command_groups:
            sub_names = sub_group.name.split(" ")
            for i in range(parent_name_len, len(sub_names)):
                yield sub_names[:i+1]
            for names in self.iter_command_group_names(parent=sub_group):
                yield names

    def find_command_group(self, *cg_names, parent=None):
        parent = parent or self.cfg
        if not cg_names:
            return None, None, parent, []
        cg_names = [*cg_names]

        group = None
        names = None
        if parent.command_groups:
            for sub_group in parent.command_groups:
                sub_names = sub_group.name.split(" ")
                if len(sub_names) < len(cg_names) and sub_names == cg_names[:len(sub_names)] or \
                        len(sub_names) >= len(cg_names) and sub_names[:len(cg_names)] == cg_names:
                    assert group is None and names is None, "multiple match found"
                    group = sub_group
                    names = sub_names

        if not group:
            return None, None, parent, cg_names

        if len(names) >= len(cg_names):
            tail_names = names[len(cg_names):]
            return group, tail_names, parent, cg_names

        return self.find_command_group(*cg_names[len(names):], parent=group)

    def find_command(self, *cmd_names):
        if len(cmd_names) < 2:
            return None
        cmd_names = [*cmd_names]

        command_group, tail_names, _, _ = self.find_command_group(*cmd_names[:-1])
        if command_group is None or tail_names:
            # group is not match cmd_names[:-1]
            return None
        name = cmd_names[-1]
        if command_group.commands:
            for command in command_group.commands:
                if command.name == name:
                    return command
        return None

    # command specific

    # arg operations
    def find_arg(self, *cmd_names, idx):
        command = self.find_command(*cmd_names)
        if not command:
            return None
        return self.find_arg_in_command(command, idx)

    @classmethod
    def find_arg_in_command(cls, command, idx):
        if isinstance(idx, str):
            idx = cls.arg_idx_to_list(idx)
        assert isinstance(idx, list), f"invalid arg_idx type: {type(idx)}"

        if command.arg_groups:
            for arg_group in command.arg_groups:
                arg = cls.find_arg_in_group(arg_group, idx)
                if arg:
                    return arg

        return None

    def find_arg_parent(self, *cmd_names, idx):
        command = self.find_command(*cmd_names)
        if not command:
            return None, None

        return self.find_arg_parent_in_command(command, idx)

    @classmethod
    def find_arg_parent_in_command(cls, command, idx):
        if isinstance(idx, str):
            idx = cls.arg_idx_to_list(idx)
        assert isinstance(idx, list), f"invalid arg_idx type: {type(idx)}"

        if len(idx) == 1:
            if command.arg_groups:
                for arg_group in command.arg_groups:
                    if cls.find_arg_in_group(arg_group, idx) is not None:
                        return None, arg_group
        else:
            parent_idx = idx[:-1]
            parent_arg = cls.find_arg_in_command(command, idx=parent_idx)
            if parent_arg is not None:
                return parent_idx, parent_arg
        return None, None

    @classmethod
    def find_arg_in_group(cls, arg_group, idx):
        assert isinstance(arg_group, CMDArgGroup)

        if isinstance(idx, str):
            idx = cls.arg_idx_to_list(idx)
        assert isinstance(idx, list) and len(idx) > 0

        current_idx = idx[0]
        remain_idx = idx[1:]
        for arg in arg_group.args:
            if current_idx in arg.options:
                if not remain_idx:
                    return arg
                return cls.find_sub_arg(arg, remain_idx)
        return None

    @classmethod
    def find_sub_arg(cls, arg, idx):
        if isinstance(idx, str):
            idx = cls.arg_idx_to_list(idx)
        assert isinstance(idx, list) and len(idx) > 0

        if isinstance(arg, CMDObjectArgBase):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if current_idx == '{}':
                if arg.additional_props and arg.additional_props.item:
                    item = arg.additional_props.item
                    if not remain_idx:
                        return item
                    return cls.find_sub_arg(item, remain_idx)
            elif arg.args:
                for sub_arg in arg.args:
                    if current_idx in sub_arg.options:
                        if not remain_idx:
                            return sub_arg
                        return cls.find_sub_arg(sub_arg, remain_idx)

        elif isinstance(arg, CMDArrayArgBase):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if current_idx == '[]':
                item = arg.item
                if not remain_idx:
                    return item
                return cls.find_sub_arg(item, remain_idx)

        return None

    def find_arg_by_var(self, *cmd_names, arg_var):
        command = self.find_command(*cmd_names)
        if not command:
            return None, None
        return self.find_arg_in_command_by_var(command, arg_var=arg_var)

    def find_arg_with_parent_by_var(self, *cmd_names, arg_var):
        """
        :return: (parent, arg_idx, arg)
            parent: argument or arg_group
            arg_idx: argument idx in string
            arg: matched argument

            if argument is not flatten, return parent, arg_idx, arg
            else if argument is flatten, return parent, None, None
            else if argument is not exist, return None, None, None

        """
        command = self.find_command(*cmd_names)
        if not command:
            return None, None, None
        return self.find_arg_in_command_with_parent_by_var(command, arg_var=arg_var)

    @classmethod
    def find_arg_in_command_by_var(cls, command, arg_var):
        _, arg, arg_idx = cls.find_arg_in_command_with_parent_by_var(command, arg_var=arg_var)
        return arg, arg_idx

    @classmethod
    def find_arg_in_command_with_parent_by_var(cls, command, arg_var):
        assert isinstance(arg_var, str), f"invalid arg_var type: {type(arg_var)}"

        def arg_filter(_parent, _arg, _arg_idx, _arg_var):
            if arg_var == _arg_var:
                # find match
                return (_parent, _arg, _arg_idx, _arg_var), True
            elif _arg_var.startswith(f'{arg_var}.'):
                # arg_var already been flattened
                return (_parent, None, None, None), True
            return None, False

        if command.arg_groups:
            for arg_group in command.arg_groups:
                matches = [match for match in cls._iter_args_in_group(
                    arg_group, arg_filter=arg_filter
                )]
                if not matches:
                    continue
                assert len(matches) == 1

                parent, arg, arg_idx, arg_var = matches[0]
                if arg:
                    arg_idx = cls.arg_idx_to_str(arg_idx)
                return parent, arg, arg_idx

        return None, None, None

    @classmethod
    def is_similar_args(cls, arg1, arg2):
        if set(arg1.options) != set(arg2.options):
            return False
        if arg1.stage != arg2.stage:
            return False
        if arg1.hide != arg2.hide:
            return False

        return cls._is_similar_args_in_base(arg1, arg2)

    @classmethod
    def _is_similar_args_in_base(cls, arg1, arg2):
        if isinstance(arg1, CMDArrayArgBase) and isinstance(arg2, CMDArrayArgBase):
            return cls._is_similar_args_in_base(arg1.item, arg2.item)
        elif isinstance(arg1, CMDObjectArgBase) and isinstance(arg2, CMDObjectArgBase):
            # verify args
            if (not arg1.args) != (not arg2.args):
                return False
            if arg1.args:
                if len(arg1.args) != len(arg2.args):
                    return False
                for sub_arg1 in arg1.args:
                    find_match = False
                    for sub_arg2 in arg2.args:
                        if cls.is_similar_args(sub_arg1, sub_arg2):
                            find_match = True
                            break
                    if not find_match:
                        return False

            # verify additional props
            if (arg1.additional_props is not None) != (arg2.additional_props is not None):
                return False
            if arg1.additional_props:
                if (arg1.additional_props.item is not None) != (arg2.additional_props.item is not None):
                    return False
                if arg1.additional_props.item:
                    if not cls._is_similar_args_in_base(arg1.additional_props.item, arg2.additional_props.item):
                        return False
        elif arg1.type != arg2.type:
            # handle cls argument
            if arg1.type.startswith("@") and arg1.type == getattr(arg2, 'cls', None):
                return True
            if arg2.type.startswith("@") and arg2.type == getattr(arg1, 'cls', None):
                return True
            return False
        return True

    def find_arg_cls_definition(self, *cmd_names, cls_name):
        command = self.find_command(*cmd_names)
        if not command:
            return None, None, None, None
        return self._find_arg_cls_definition(command, cls_name)

    @classmethod
    def _find_arg_cls_definition(cls, command, cls_name):

        assert isinstance(cls_name, str) and not cls_name.startswith('@')

        def arg_filter(_parent, _arg, _arg_idx, _arg_var):
            if getattr(_arg, 'cls', None) == cls_name:
                # find match
                return (_parent, _arg, _arg_idx, _arg_var), True
            return None, False

        if command.arg_groups:
            for arg_group in command.arg_groups:
                matches = [match for match in cls._iter_args_in_group(
                    arg_group, arg_filter=arg_filter
                )]
                if not matches:
                    continue
                assert len(matches) == 1

                parent, arg, arg_idx, arg_var = matches[0]
                if arg:
                    arg_idx = cls.arg_idx_to_str(arg_idx)
                return parent, arg, arg_idx, arg_var

        return None, None, None, None

    def iter_arg_cls_definition(self, *cmd_names, cls_name_prefix=None):
        command = self.find_command(*cmd_names)
        if not command:
            return

        for match in self._iter_arg_cls_definition(command, cls_name_prefix=cls_name_prefix):
            yield match

    @classmethod
    def _iter_arg_cls_definition(cls, command, cls_name_prefix=None):
        if cls_name_prefix is not None:
            assert isinstance(cls_name_prefix, str) and not cls_name_prefix.startswith('@')
            if not cls_name_prefix.endswith('_'):
                # make sure cls_name_prefix ends with '_' to match
                # `<cls>_create`, `<cls>_update` kind cls_name only
                cls_name_prefix += '_'

        def arg_filter(_parent, _arg, _arg_idx, _arg_var):
            _cls = getattr(_arg, 'cls', None)
            if _cls is not None and (cls_name_prefix is None or _cls.startswith(cls_name_prefix)):
                # find match
                return (_parent, _arg, _arg_idx, _arg_var), False
            return None, False

        if command.arg_groups:
            for arg_group in command.arg_groups:
                for parent, arg, arg_idx, arg_var in cls._iter_args_in_group(arg_group, arg_filter=arg_filter):
                    if arg:
                        arg_idx = cls.arg_idx_to_str(arg_idx)
                    yield parent, arg, arg_idx, arg_var

    def iter_arg_cls_reference(self, *cmd_names, cls_name):
        command = self.find_command(*cmd_names)
        if not command:
            return

        for match in self._iter_arg_cls_reference(command, cls_name=cls_name):
            yield match

    @classmethod
    def _iter_arg_cls_reference(cls, command, cls_name):
        assert isinstance(cls_name, str) and not cls_name.startswith('@')

        cls_type_name = f"@{cls_name}"

        def arg_filter(_parent, _arg, _arg_idx, _arg_var):
            if _arg.type == cls_type_name:
                # find match
                return (_parent, _arg, _arg_idx, _arg_var), False
            return None, False

        if command.arg_groups:
            for arg_group in command.arg_groups:
                for parent, arg, arg_idx, arg_var in cls._iter_args_in_group(
                        arg_group, arg_filter=arg_filter):
                    if arg:
                        arg_idx = cls.arg_idx_to_str(arg_idx)
                    yield parent, arg, arg_idx, arg_var

    def iter_args_in_command(self, command):
        def arg_filter(_parent, _arg, _arg_idx, _arg_var):
            return (_parent, _arg, _arg_idx, _arg_var), False

        if command.arg_groups:
            for arg_group in command.arg_groups:
                for parent, arg, arg_idx, arg_var in self._iter_args_in_group(arg_group, arg_filter=arg_filter):
                    if arg:
                        arg_idx = self.arg_idx_to_str(arg_idx)
                    yield parent, arg, arg_idx, arg_var

    # TODO: build arg_idx in command link call
    @classmethod
    def _iter_args_in_group(cls, arg_group, arg_filter):
        assert isinstance(arg_group, CMDArgGroup)
        for arg in arg_group.args:
            arg_option = max(arg.options, key=lambda item: len(item))
            match, ret = arg_filter(arg_group, arg, [arg_option], arg.var)
            if match:
                yield match
            if ret:
                return

            for sub_parent, sub_arg, sub_arg_idx, sub_arg_var in cls._iter_sub_args(arg, arg.var, arg_filter):
                if sub_arg_idx:
                    sub_arg_idx = [arg_option, *sub_arg_idx]
                yield sub_parent, sub_arg, sub_arg_idx, sub_arg_var

    @classmethod
    def _iter_sub_args(cls, parent, arg_var, arg_filter):
        if isinstance(parent, CMDObjectArgBase):
            if parent.args:
                for arg in parent.args:
                    arg_option = max(arg.options, key=lambda item: len(item))
                    match, ret = arg_filter(parent, arg, [arg_option], arg.var)
                    if match:
                        yield match
                    if ret:
                        return

                    for sub_parent, sub_arg, sub_arg_idx, sub_arg_var in cls._iter_sub_args(arg, arg.var, arg_filter):
                        if sub_arg:
                            sub_arg_idx = [arg_option, *sub_arg_idx]
                        yield sub_parent, sub_arg, sub_arg_idx, sub_arg_var

            if parent.additional_props and parent.additional_props.item:
                item = parent.additional_props.item
                item_var = arg_var + '{}'

                match, ret = arg_filter(parent, item, ['{}'], item_var)
                if match:
                    yield match
                if ret:
                    return

                for sub_parent, sub_arg, sub_arg_idx, sub_arg_var in cls._iter_sub_args(item, item_var, arg_filter):
                    if sub_arg:
                        sub_arg_idx = ['{}', *sub_arg_idx]
                    yield sub_parent, sub_arg, sub_arg_idx, sub_arg_var

        elif isinstance(parent, CMDArrayArgBase):
            item = parent.item
            item_var = arg_var + '[]'

            match, ret = arg_filter(parent, item, ['[]'], item_var)
            if match:
                yield match
            if ret:
                return

            for sub_parent, sub_arg, sub_arg_idx, sub_arg_var in cls._iter_sub_args(item, item_var, arg_filter):
                if sub_arg:
                    sub_arg_idx = ['[]', *sub_arg_idx]
                yield sub_parent, sub_arg, sub_arg_idx, sub_arg_var

    @staticmethod
    def arg_idx_to_list(arg_idx):
        if isinstance(arg_idx, list):
            return arg_idx
        assert isinstance(arg_idx, str)
        # arg_idx will not contain '{Key}' or '[Index]'
        arg_idx = arg_idx.replace('{}', '.{}').replace('[]', '.[]').split('.')
        return [idx for idx in arg_idx if idx]

    @staticmethod
    def arg_idx_to_str(arg_idx):
        if isinstance(arg_idx, str):
            return arg_idx
        assert isinstance(arg_idx, list)
        # arg_idx will not contain '{Key}' or '[Index]'
        return '.'.join(arg_idx).replace('.{}', '{}').replace('.[]', '[]')

    # schema operations
    def find_schema(self, *cmd_names, idx):
        command = self.find_command(*cmd_names)
        if not command:
            return None
        return self.find_schema_in_command(command, idx)

    @classmethod
    def find_schema_in_command(cls, command, idx):
        assert isinstance(idx, list), f"invalid schema_idx type: {type(idx)}"
        for op in command.operations:
            schema = cls.find_schema_in_operation(op, idx)
            if schema:
                return schema
        return None

    @classmethod
    def find_schema_in_operation(cls, operation, idx):
        assert isinstance(idx, list), f"invalid schema_idx type: {type(idx)}"
        current_idx, next_idx = idx[:2]
        remain_idx = idx[2:]

        if isinstance(operation, CMDHttpOperation) and current_idx == _SchemaIdxEnum.Http:
            if operation.http.request and next_idx == _SchemaIdxEnum.Request:
                schema = cls.find_schema_in_request(operation.http.request, remain_idx)
                if schema:
                    return schema
            if operation.http.responses and next_idx.startswith(_SchemaIdxEnum.Response):
                for response in operation.http.responses:
                    if response.is_error:
                        continue
                    if '_'.join([_SchemaIdxEnum.Response, *[str(code) for code in response.status_codes]]) == next_idx:
                        schema = cls.find_schema_in_response(response, remain_idx)
                        if schema:
                            return schema

        elif isinstance(operation, CMDInstanceCreateOperation) and current_idx == _SchemaIdxEnum.Instance and next_idx == _SchemaIdxEnum.Create:
            if isinstance(operation.instance_create, CMDJsonInstanceCreateAction) and remain_idx[0] == _SchemaIdxEnum.Json:
                schema = cls.find_schema_in_json(operation.instance_create.json, remain_idx[1:])
                if schema:
                    return schema

        elif isinstance(operation, CMDInstanceUpdateOperation) and current_idx == _SchemaIdxEnum.Instance and next_idx == _SchemaIdxEnum.Update:
            if isinstance(operation.instance_update, CMDJsonInstanceUpdateAction) and remain_idx[0] == _SchemaIdxEnum.Json:
                schema = cls.find_schema_in_json(operation.instance_update.json, remain_idx[1:])
                if schema:
                    return schema

        return None

    def find_schema_parent(self, *cmd_names, idx):
        command = self.find_command(*cmd_names)
        if not command:
            return None, None
        return self.find_schema_parent_in_command(command, idx)

    @classmethod
    def find_schema_parent_in_command(cls, command, idx):
        assert isinstance(idx, list), f"invalid schema_idx type: {type(idx)}"
        parent_idx = idx[:-1]
        parent_schema = cls.find_schema_in_command(command, idx=parent_idx)
        if parent_schema is not None:
            return parent_idx, parent_schema
        return None, None

    @classmethod
    def find_schema_in_request(cls, request, idx):
        current_idx = idx[0]
        remain_idx = idx[1:]
        if request.path and current_idx == _SchemaIdxEnum.Path:
            if remain_idx and request.path.params:
                for param in request.path.params:
                    if param.name == remain_idx[0]:
                        return param

        if request.query and current_idx == _SchemaIdxEnum.Query:
            if remain_idx and request.query.params:
                for param in request.query.params:
                    if param.name == remain_idx[0]:
                        return param

        if request.header and current_idx == _SchemaIdxEnum.Header:
            if remain_idx and request.header.params:
                for param in request.header.params:
                    if param.name == remain_idx[0]:
                        return param

        if isinstance(request.body, CMDHttpRequestJsonBody) and current_idx == _SchemaIdxEnum.Body:
            current_idx = remain_idx[0]
            remain_idx = remain_idx[1:]
            if current_idx == _SchemaIdxEnum.Json:
                return cls.find_schema_in_json(request.body.json, remain_idx)
        return None

    @classmethod
    def find_schema_in_response(cls, response, idx):
        if isinstance(response.body, CMDHttpResponseJsonBody):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if current_idx == _SchemaIdxEnum.Json:
                return cls.find_schema_in_json(response.body.json, remain_idx)
        return None

    @classmethod
    def find_schema_in_json(cls, js, idx):
        assert isinstance(js, (CMDRequestJson, CMDResponseJson))
        if not idx:
            return js.schema
        if idx:
            return cls.find_sub_schema(js.schema, idx)
        return None

    @classmethod
    def find_sub_schema(cls, schema, idx):
        assert isinstance(idx, list) and len(idx) > 0

        if isinstance(schema, CMDObjectSchemaBase):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if current_idx == '{}':
                if schema.additional_props and schema.additional_props.item:
                    item = schema.additional_props.item
                    if not remain_idx:
                        return item
                    return cls.find_sub_schema(item, remain_idx)
            elif schema.props:
                for prop in schema.props:
                    if current_idx == prop.name:
                        if not remain_idx:
                            return prop
                        return cls.find_sub_schema(prop, remain_idx)

            elif schema.discriminators:
                for disc in schema.discriminators:
                    if current_idx == disc.get_safe_value():
                        if not remain_idx:
                            return disc
                        return cls.find_sub_schema(disc, remain_idx)

        elif isinstance(schema, CMDObjectSchemaDiscriminator):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if schema.props:
                for prop in schema.props:
                    if current_idx == prop.name:
                        if not remain_idx:
                            return prop
                        return cls.find_sub_schema(prop, remain_idx)

            elif schema.discriminators:
                for disc in schema.discriminators:
                    if current_idx == disc.get_safe_value():
                        if not remain_idx:
                            return disc
                        return cls.find_sub_schema(disc, remain_idx)

        elif isinstance(schema, CMDArraySchemaBase):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if current_idx == '[]':
                item = schema.item
                if not remain_idx:
                    return item
                return cls.find_sub_schema(item, remain_idx)

        return None

    @classmethod
    def iter_schema_in_command_by_arg_var(cls, command, arg_var):
        for operation in command.operations:
            for match in cls.iter_schema_in_operation_by_arg_var(operation, arg_var):
                yield match

    @classmethod
    def iter_schema_in_operation_by_arg_var(cls, operation, arg_var):
        def schema_filter(_parent, _schema, _schema_idx):
            if isinstance(_schema, CMDSchema):
                if _schema.arg == arg_var:
                    # find match
                    return (_parent, _schema, _schema_idx), False
            elif isinstance(_schema, CMDSchemaBase):
                if arg_var.endswith('[]') and _schema_idx[-1] == '[]' and \
                        isinstance(_parent, CMDArraySchema) and _parent.arg == arg_var[:-2]:
                    # find match
                    return (_parent, _schema, _schema_idx), False
                elif arg_var.endswith('{}') and _schema_idx[-1] == '{}' and \
                        isinstance(_parent, CMDObjectSchema) and _parent.arg == arg_var[:-2]:
                    # find match
                    return (_parent, _schema, _schema_idx), False
            return None, False

        if isinstance(operation, CMDHttpOperation) and operation.http.request:
            for parent, schema, schema_idx in cls._iter_schema_in_request(
                    operation.http.request, schema_filter=schema_filter):
                if schema:
                    schema_idx = [_SchemaIdxEnum.Http, _SchemaIdxEnum.Request, *schema_idx]
                yield parent, schema, schema_idx

        if isinstance(operation, CMDInstanceUpdateOperation):
            if isinstance(operation.instance_update, CMDJsonInstanceUpdateAction):
                for parent, schema, schema_idx in cls._iter_schema_in_json(
                        operation.instance_update.json, schema_filter=schema_filter):
                    if schema:
                        schema_idx = [_SchemaIdxEnum.Instance, _SchemaIdxEnum.Update, *schema_idx]
                    yield parent, schema, schema_idx

        if isinstance(operation, CMDInstanceCreateOperation):
            if isinstance(operation.instance_create, CMDJsonInstanceCreateAction):
                for parent, schema, schema_idx in cls._iter_schema_in_json(
                        operation.instance_create.json, schema_filter=schema_filter):
                    if schema:
                        schema_idx = [_SchemaIdxEnum.Instance, _SchemaIdxEnum.Create, *schema_idx]
                    yield parent, schema, schema_idx

    @classmethod
    def iter_schema_cls_reference(cls, command, cls_name):
        for match in cls.iter_schema_cls_reference_in_operations(command.operations, cls_name):
            yield match

    @classmethod
    def iter_schema_cls_reference_in_operations(cls, operations, cls_name):
        assert isinstance(cls_name, str) and not cls_name.startswith('@')

        cls_type_name = f"@{cls_name}"

        def schema_filter(_parent, _schema, _schema_idx):
            if _schema.type == cls_type_name:
                # find match
                return (_parent, _schema, _schema_idx), False
            return None, False

        for op in operations:
            if isinstance(op, CMDHttpOperation):
                if op.http.request:
                    for parent, schema, schema_idx in cls._iter_schema_in_request(op.http.request, schema_filter=schema_filter):
                        if schema:
                            schema_idx = [_SchemaIdxEnum.Http, _SchemaIdxEnum.Request, *schema_idx]
                        yield parent, schema, schema_idx
                if op.http.responses:
                    for response in op.http.responses:
                        if response.is_error:
                            continue
                        schema_idx_prefix = [_SchemaIdxEnum.Http, '_'.join([_SchemaIdxEnum.Response, *[str(code) for code in response.status_codes]])]
                        for parent, schema, schema_idx in cls._iter_schema_in_response(response, schema_filter=schema_filter):
                            if schema:
                                schema_idx = [*schema_idx_prefix, *schema_idx]
                            yield parent, schema, schema_idx

            if isinstance(op, CMDInstanceUpdateOperation):
                if isinstance(op.instance_update, CMDJsonInstanceUpdateAction):
                    for parent, schema, schema_idx in cls._iter_schema_in_json(op.instance_update.json, schema_filter=schema_filter):
                        if schema:
                            schema_idx = [_SchemaIdxEnum.Instance, _SchemaIdxEnum.Update, *schema_idx]
                        yield parent, schema, schema_idx

            if isinstance(op, CMDInstanceCreateOperation):
                if isinstance(op.instance_create, CMDJsonInstanceCreateAction):
                    for parent, schema, schema_idx in cls._iter_schema_in_json(op.instance_create.json, schema_filter=schema_filter):
                        if schema:
                            schema_idx = [_SchemaIdxEnum.Instance, _SchemaIdxEnum.Create, *schema_idx]
                        yield parent, schema, schema_idx

    @classmethod
    def iter_schema_cls_reference_in_schema(cls, schema, cls_name):
        assert isinstance(cls_name, str) and not cls_name.startswith('@')

        cls_type_name = f"@{cls_name}"

        def schema_filter(_parent, _schema, _schema_idx):
            if _schema.type == cls_type_name:
                # find match
                return (_parent, _schema, _schema_idx), False
            return None, False

        for match in cls._iter_sub_schema(schema, schema_filter):
            yield match

    # TODO: build schema_idx in command link call
    @classmethod
    def _iter_schema_in_request(cls, request, schema_filter):
        if request.path and request.path.params:
            for param in request.path.params:
                match, ret = schema_filter(request.path, param, [_SchemaIdxEnum.Path, param.name])
                if match:
                    yield match
                if ret:
                    return

        if request.query and request.query.params:
            for param in request.query.params:
                match, ret = schema_filter(request.query, param, [_SchemaIdxEnum.Query, param.name])
                if match:
                    yield match
                if ret:
                    return

        if request.header and request.header.params:
            for param in request.header.params:
                match, ret = schema_filter(request.header, param, [_SchemaIdxEnum.Header, param.name])
                if match:
                    yield match
                if ret:
                    return

        if isinstance(request.body, CMDHttpRequestJsonBody):
            for parent, schema, schema_idx in cls._iter_schema_in_json(request.body.json, schema_filter):
                if schema:
                    schema_idx = [_SchemaIdxEnum.Body, *schema_idx]
                yield parent, schema, schema_idx

    @classmethod
    def _iter_schema_in_response(cls, response, schema_filter):
        if isinstance(response.body, CMDHttpResponseJsonBody):
            for parent, schema, schema_idx in cls._iter_schema_in_json(response.body.json, schema_filter):
                if schema:
                    schema_idx = [_SchemaIdxEnum.Body, *schema_idx]
                yield parent, schema, schema_idx

    @classmethod
    def _iter_schema_in_json(cls, js, schema_filter):
        assert isinstance(js, (CMDRequestJson, CMDResponseJson))
        if js.schema is None:
            return
        match, ret = schema_filter(js, js.schema, [_SchemaIdxEnum.Json])
        if match:
            yield match
        if ret:
            return

        # if isinstance(js.schema, (CMDObjectSchemaBase, CMDArraySchemaBase)):
        for parent, schema, schema_idx in cls._iter_sub_schema(js.schema, schema_filter):
            if schema:
                schema_idx = [_SchemaIdxEnum.Json, *schema_idx]
            yield parent, schema, schema_idx

    @classmethod
    def _iter_sub_schema(cls, parent, schema_filter):
        if isinstance(parent, CMDObjectSchemaBase):
            if parent.props:
                for prop in parent.props:
                    match, ret = schema_filter(parent, prop, [prop.name])
                    if match:
                        yield match
                    if ret:
                        return

                    # if isinstance(prop, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    for sub_parent, sub_schema, sub_schema_idx in cls._iter_sub_schema(prop, schema_filter):
                        if sub_schema:
                            sub_schema_idx = [prop.name, *sub_schema_idx]
                        yield sub_parent, sub_schema, sub_schema_idx

            if parent.additional_props and parent.additional_props.item:
                item = parent.additional_props.item
                match, ret = schema_filter(parent, item, ['{}'])
                if match:
                    yield match
                if ret:
                    return

                for sub_parent, sub_schema, sub_schema_idx in cls._iter_sub_schema(item, schema_filter):
                    if sub_schema:
                        sub_schema_idx = ['{}', *sub_schema_idx]
                    yield sub_parent, sub_schema, sub_schema_idx

            if parent.discriminators:
                for disc in parent.discriminators:
                    for sub_parent, sub_schema, sub_schema_idx in cls._iter_sub_schema(disc, schema_filter):
                        if sub_schema:
                            sub_schema_idx = [disc.get_safe_value(), *sub_schema_idx]
                        yield sub_parent, sub_schema, sub_schema_idx

        elif isinstance(parent, CMDObjectSchemaDiscriminator):
            if parent.props:
                for prop in parent.props:
                    match, ret = schema_filter(parent, prop, [prop.name])
                    if match:
                        yield match
                    if ret:
                        return

                    # if isinstance(prop, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    for sub_parent, sub_schema, sub_schema_idx in cls._iter_sub_schema(prop, schema_filter):
                        if sub_schema:
                            sub_schema_idx = [prop.name, *sub_schema_idx]
                        yield sub_parent, sub_schema, sub_schema_idx

            if parent.discriminators:
                for disc in parent.discriminators:
                    for sub_parent, sub_schema, sub_schema_idx in cls._iter_sub_schema(disc, schema_filter):
                        if sub_schema:
                            sub_schema_idx = [disc.get_safe_value(), *sub_schema_idx]
                        yield sub_parent, sub_schema, sub_schema_idx

        elif isinstance(parent, CMDArraySchemaBase):
            item = parent.item
            match, ret = schema_filter(parent, item, ['[]'])
            if match:
                yield match
            if ret:
                return

            for sub_parent, sub_schema, sub_schema_idx in cls._iter_sub_schema(item, schema_filter):
                if sub_schema:
                    sub_schema_idx = ['[]', *sub_schema_idx]
                yield sub_parent, sub_schema, sub_schema_idx

    @classmethod
    def schema_idx_to_subresource_idx(cls, schema_idx):
        for i, idx in enumerate(schema_idx):
            if idx == _SchemaIdxEnum.Json:
                return [*schema_idx[i+1:]]
        return None

    @staticmethod
    def idx_to_list(subresource_idx):
        if isinstance(subresource_idx, list):
            return subresource_idx
        assert isinstance(subresource_idx, str)
        subresource_idx = subresource_idx.replace('{}', '.{}').replace('[]', '.[]').split('.')
        return [idx for idx in subresource_idx if idx]

    @staticmethod
    def idx_to_str(subresource_idx):
        if isinstance(subresource_idx, str):
            return subresource_idx
        assert isinstance(subresource_idx, list)
        return '.'.join(subresource_idx).replace('.{}', '{}').replace('.[]', '[]')
