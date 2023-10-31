from command.model.configuration import CMDCommandExample
from swagger.model.schema.example_item import XmsExamplesField
from swagger.model.schema.path_item import PathItem
from swagger.model.specs import SwaggerLoader


class ExampleGenerator:
    def __init__(self):
        self.loader = SwaggerLoader()

    def load_examples(self, resource, operation_id):
        self.loader.load_file(resource.file_path)
        self.loader.link_examples(resource.file_path, resource.path, operation_id)

    def create_draft_examples(self, resource, operation_id, cmd_name):
        swagger = self.loader.get_loaded(resource.file_path)
        assert swagger is not None

        path_item = swagger.paths.get(resource.path, None)
        if path_item is None:
            path_item = swagger.x_ms_paths.get(resource.path, None)
        assert isinstance(path_item, PathItem)

        linked_examples = XmsExamplesField()
        if path_item.get is not None and operation_id == path_item.get.operation_id:
            linked_examples = path_item.get.x_ms_examples
        elif path_item.delete is not None and operation_id == path_item.delete.operation_id:
            linked_examples = path_item.delete.x_ms_examples
        elif path_item.put is not None and operation_id == path_item.put.operation_id:
            linked_examples = path_item.put.x_ms_examples
        elif path_item.post is not None and operation_id == path_item.post.operation_id:
            linked_examples = path_item.post.x_ms_examples
        elif path_item.head is not None and operation_id == path_item.head.operation_id:
            linked_examples = path_item.head.x_ms_examples

        cmd_examples = []
        for name, example_item in linked_examples.items():
            example = example_item.to_cmd(cmd_name)
            example.name = name
            cmd_examples.append(example)

        return cmd_examples
