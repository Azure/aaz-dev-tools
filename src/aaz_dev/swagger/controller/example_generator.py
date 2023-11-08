from command.model.configuration import CMDCommandExample
from swagger.model.schema.example_item import XmsExamplesField
from swagger.model.schema.path_item import PathItem
from swagger.model.specs import SwaggerLoader


class ExampleGenerator:
    def __init__(self):
        self.loader = SwaggerLoader()

    def load_examples(self, resources, operation_ids):
        for resource in resources:
            self.loader.load_file(resource.file_path)
            self.loader.link_examples(resource.file_path, resource.path, operation_ids)

    def create_draft_examples(self, resources, operation_ids, cmd_name, arg_groups):
        cmd_examples = []
        arg_name_map = get_arg_name_map(arg_groups)

        for resource in resources:
            swagger = self.loader.get_loaded(resource.file_path)
            if not swagger:
                continue

            path_item = swagger.paths.get(resource.path, None)
            if path_item is None:
                path_item = swagger.x_ms_paths.get(resource.path, None)
            if not isinstance(path_item, PathItem):
                continue

            linked_examples = XmsExamplesField()
            if path_item.get is not None and path_item.get.operation_id in operation_ids:
                linked_examples = path_item.get.x_ms_examples
            elif path_item.delete is not None and path_item.delete.operation_id in operation_ids:
                linked_examples = path_item.delete.x_ms_examples
            elif path_item.put is not None and path_item.put.operation_id in operation_ids:
                linked_examples = path_item.put.x_ms_examples
            elif path_item.post is not None and path_item.post.operation_id in operation_ids:
                linked_examples = path_item.post.x_ms_examples
            elif path_item.head is not None and path_item.head.operation_id in operation_ids:
                linked_examples = path_item.head.x_ms_examples

            for name, example_item in linked_examples.items():
                example = example_item.to_cmd(arg_name_map, cmd_name)
                example.name = name
                cmd_examples.append(example)

        return cmd_examples


def get_arg_name_map(arg_groups):
    IGNORE_ARGS = ["subscriptionId"]

    arg_name_map = {}
    for group in arg_groups:
        for arg in group.args:
            swagger_name = arg.var.split(".", maxsplit=1)[-1]
            if swagger_name in IGNORE_ARGS:
                continue

            arg_name = arg.options[-1]
            arg_name = "-" + arg_name if len(arg_name) == 1 else "--" + arg_name

            arg_name_map[swagger_name] = arg_name

    return arg_name_map
