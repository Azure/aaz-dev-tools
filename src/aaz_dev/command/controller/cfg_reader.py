import json

from command.model.configuration import CMDConfiguration, CMDHttpOperation, CMDInstanceUpdateOperation, \
    CMDCommandGroup, CMDArgGroup, CMDObjectArg, CMDArrayArg, CMDObjectArgBase, CMDArrayArgBase


class CfgReader:

    def __init__(self, cfg):
        assert isinstance(cfg, CMDConfiguration)
        self.cfg = cfg

    @property
    def resources(self):
        return self.cfg.resources

    def iter_cfg_files_data(self):
        main_resource = self.cfg.resources[0]
        data = json.dumps(self.cfg.to_primitive(), ensure_ascii=False)
        yield main_resource.id, data
        for resource in self.cfg.resources[1:]:
            assert resource.version == main_resource.version
            data = json.dumps({"$ref": main_resource.id}, ensure_ascii=False)
            yield resource.id, data

    def iter_commands(self):
        groups = []
        for group in self.cfg.command_groups:
            groups.append((group.name.split(" "), group))
        idx = 0
        while idx < len(groups):
            node_names, command_group = groups[idx]
            assert isinstance(command_group, CMDCommandGroup)
            if command_group.commands:
                for command in command_group.commands:
                    yield [*node_names, command.name], command
            if command_group.command_groups:
                for group in command_group.command_groups:
                    groups.append(([*node_names, group.name], group))
            idx += 1

    def iter_commands_by_resource(self, resource_id, version=None):
        for cmd_name, command in self.iter_commands():
            for r in command.resources:
                if r.id == resource_id and (not version or r.version == version):
                    yield cmd_name, command
                    break

    def iter_commands_by_operations(self, *methods):
        # use 'update' as the methods of instance update operation
        methods = {m.lower() for m in methods}
        for cmd_names, command in self.iter_commands():
            ops_methods = set()
            has_extra_methods = False
            for operation in command.operations:
                if isinstance(operation, CMDInstanceUpdateOperation):
                    if 'update' not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add('update')
                elif isinstance(operation, CMDHttpOperation):
                    http = operation.http
                    if http.request.method.lower() not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add(http.request.method.lower())
            if not has_extra_methods and ops_methods == methods:
                yield cmd_names, command

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

    # command

    def find_arg(self, *cmd_names, idx):
        command = self.find_command(*cmd_names)
        if not command:
            return None

        if isinstance(idx, str):
            idx = self.arg_idx_to_list(idx)
        assert isinstance(idx, list), f"invalid arg_idx type: {type(idx)}"

        for arg_group in command.arg_groups:
            arg = self._find_arg_in_group(arg_group, idx)
            if arg:
                return arg

        return None

    def find_arg_parent(self, *cmd_names, idx):
        command = self.find_command(*cmd_names)
        if not command:
            return None, None

        if isinstance(idx, str):
            idx = self.arg_idx_to_list(idx)
        assert isinstance(idx, list), f"invalid arg_idx type: {type(idx)}"

        if len(idx) == 1:
            for arg_group in command.arg_groups:
                if self._find_arg_in_group(arg_group, idx) is not None:
                    return None, arg_group
        else:
            parent_idx = idx[:-1]
            parent_arg = self.find_arg(*cmd_names, idx=parent_idx)
            if parent_arg is not None:
                return parent_idx, parent_arg
        return None, None

    def _find_arg_in_group(self, arg_group, idx):
        assert isinstance(arg_group, CMDArgGroup)
        current_idx = idx[0]
        remain_idx = idx[1:]
        for arg in arg_group.args:
            if current_idx in arg.options:
                if not remain_idx:
                    return arg
                return self._find_sub_arg(arg, remain_idx)
        return None

    def _find_sub_arg(self, arg, idx):
        assert isinstance(idx, list) and len(idx) > 0
        if isinstance(arg, CMDObjectArgBase):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if current_idx == '{}':
                if arg.additional_props and arg.additional_props.item:
                    item = arg.additional_props.item
                    if not remain_idx:
                        return item
                    return self._find_sub_arg(item, remain_idx)
            elif arg.args:
                for sub_arg in arg.args:
                    if current_idx in sub_arg.options:
                        if not remain_idx:
                            return sub_arg
                        return self._find_sub_arg(sub_arg, remain_idx)

        elif isinstance(arg, CMDArrayArgBase):
            current_idx = idx[0]
            remain_idx = idx[1:]
            if current_idx == '[]':
                item = arg.item
                if not remain_idx:
                    return item
                return self._find_sub_arg(item, remain_idx)

        return None

    def find_arg_by_var(self, *cmd_names, arg_var):
        _, arg_idx, arg = self.find_arg_with_parent_by_var(*cmd_names, arg_var=arg_var)
        return arg_idx, arg

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
        assert isinstance(arg_var, str), f"invalid arg_var type: {type(arg_var)}"

        for arg_group in command.arg_groups:
            parent, arg_idx, arg = self._find_arg_in_group_by_var(arg_group, arg_var)
            if arg or parent:
                if arg_idx:
                    arg_idx = self.arg_idx_to_str(arg_idx)
                return parent, arg_idx, arg
        return None, None, None

    def _find_arg_in_group_by_var(self, arg_group, arg_var):
        assert isinstance(arg_group, CMDArgGroup)
        for arg in arg_group.args:
            if arg.var == arg_var:
                # find match
                arg_idx = [arg.options[0]]
                return arg_group, arg_idx, arg
            elif arg.var.startswith(f'{arg_var}.'):
                # arg_var already been flattened
                return arg_group, None, None
            elif isinstance(arg, (CMDObjectArg, CMDArrayArg)):
                sub_parent, sub_arg_idx, sub_arg = self._find_sub_arg_by_var(arg, arg.var, arg_var)
                if sub_arg or sub_parent:
                    if sub_arg:
                        sub_arg_idx = [arg.options[0], *sub_arg_idx]
                    return sub_parent, sub_arg_idx, sub_arg
        return None, None, None

    def _find_sub_arg_by_var(self, parent, arg_var, sub_arg_var):
        assert arg_var != sub_arg_var
        if isinstance(parent, CMDObjectArgBase):
            if parent.args:
                for arg in parent.args:
                    if arg.var == sub_arg_var:
                        # find match
                        arg_idx = [arg.options[0]]
                        return parent, arg_idx, arg
                    elif arg.var.startswith(f'{sub_arg_var}.'):
                        # sub_arg_var already been flattened
                        return parent, None, None
                    elif isinstance(arg, (CMDObjectArg, CMDArrayArg)):
                        sub_parent, sub_arg_idx, sub_arg = self._find_sub_arg_by_var(arg, arg.var, sub_arg_var)
                        if sub_arg or sub_parent:
                            if sub_arg:
                                sub_arg_idx = [arg.options[0], *sub_arg_idx]
                            return sub_parent, sub_arg_idx, sub_arg

            if parent.additional_props and parent.additional_props.item:
                item = parent.additional_props.item
                item_var = arg_var + "{}"
                if item_var == sub_arg_var:
                    # find match
                    item_idx = ['{}']
                    return parent, item_idx, item

                sub_parent, sub_arg_idx, sub_arg = self._find_sub_arg_by_var(item, item_var, sub_arg_var)
                if sub_arg or sub_parent:
                    if sub_arg:
                        sub_arg_idx = ['{}', *sub_arg_idx]
                    return sub_parent, sub_arg_idx, sub_arg

        elif isinstance(parent, CMDArrayArgBase):
            item = parent.item
            item_var = arg_var + '[]'
            if item_var == sub_arg_var:
                # find match
                item_idx = ['[]']
                return parent, item_idx, item

            sub_parent, sub_arg_idx, sub_arg = self._find_sub_arg_by_var(item, item_var, sub_arg_var)
            if sub_arg or sub_parent:
                if sub_arg:
                    sub_arg_idx = ['[]', *sub_arg_idx]
                return sub_parent, sub_arg_idx, sub_arg

        return None, None, None

    def iter_similar_args(self, arg_var, arg):
        pass
    
    # def find_arg_cls_definition(self, *cmd_names, cls_name):
    #     command = self.find_command(*cmd_names)
    #     if not command:
    #         return None
    #
    #     pass

    def arg_idx_to_list(self, arg_idx):
        if isinstance(arg_idx, list):
            return arg_idx
        assert isinstance(arg_idx, str)
        arg_idx = arg_idx.replace('{}', '.{}').replace('[]', '.[]').split('.')
        return [idx for idx in arg_idx if idx]

    def arg_idx_to_str(self, arg_idx):
        if isinstance(arg_idx, str):
            return arg_idx
        assert isinstance(arg_idx, list)
        return '.'.join(arg_idx).replace('.{}', '{}').replace('.[]', '[]')
