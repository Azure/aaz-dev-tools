from command.model.configuration._example_builder import SwaggerExampleBuilder
from swagger.model.schema.cmd_builder import CMDBuilder
from swagger.model.schema.example_item import XmsExamplesField
from swagger.model.schema.fields import MutabilityEnum
from swagger.model.schema.path_item import PathItem
from swagger.model.specs import SwaggerLoader


class ExampleGenerator:
    def __init__(self):
        self.loader = SwaggerLoader()

    def load_examples(self, resources, cmd_operation_ids):
        for resource in resources:
            self.loader.load_file(resource.file_path)
            self.loader.link_examples(resource.file_path, resource.path, cmd_operation_ids)

    def create_draft_examples_by_swagger(self, resources, command, cmd_operation_ids, cmd_name):
        cmd_examples = []

        for resource in resources:
            swagger = self.loader.get_loaded(resource.file_path)
            if not swagger:
                continue

            path_item = swagger.paths.get(resource.path, None)
            if path_item is None:
                path_item = swagger.x_ms_paths.get(resource.path, None)
            if not isinstance(path_item, PathItem):
                continue

            example_builder = None
            examples = XmsExamplesField()
            if path_item.get is not None and path_item.get.operation_id in cmd_operation_ids:
                example_builder = SwaggerExampleBuilder(operation=path_item.get,
                                                        command=command)
                examples = path_item.get.x_ms_examples

            elif path_item.delete is not None and path_item.delete.operation_id in cmd_operation_ids:
                example_builder = SwaggerExampleBuilder(operation=path_item.delete,
                                                        command=command)
                examples = path_item.delete.x_ms_examples

            elif path_item.put is not None and path_item.put.operation_id in cmd_operation_ids:
                example_builder = SwaggerExampleBuilder(operation=path_item.put,
                                                        command=command)
                examples = path_item.put.x_ms_examples

            elif path_item.post is not None and path_item.post.operation_id in cmd_operation_ids:
                example_builder = SwaggerExampleBuilder(operation=path_item.post,
                                                        command=command)
                examples = path_item.post.x_ms_examples

            elif path_item.head is not None and path_item.head.operation_id in cmd_operation_ids:
                example_builder = SwaggerExampleBuilder(operation=path_item.head,
                                                        command=command)
                examples = path_item.head.x_ms_examples

            if not example_builder:
                continue

            cmd_examples.extend(self.generate_examples(cmd_name, examples, example_builder))

        return cmd_examples

    @staticmethod
    def generate_examples(cmd_name, examples, example_builder):
        cmd_examples = []
        for name, example_item in examples.items():
            cmd_example = example_item.to_cmd(example_builder, cmd_name)
            if not cmd_example:
                continue

            cmd_example.name = name
            cmd_examples.append(cmd_example)

        return cmd_examples
