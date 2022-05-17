import json

from command.model.configuration import CMDConfiguration, CMDHttpOperation, CMDInstanceUpdateOperation, CMDCommandGroup


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
