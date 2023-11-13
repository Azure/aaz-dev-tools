from command.controller.cfg_reader import CfgReader


class ExampleBuilder:
    def __init__(self, arg_groups=None):
        self.arg_groups = arg_groups

    def mapping(self, swagger_params):
        raise NotImplementedError()


class SwaggerExampleBuilder(ExampleBuilder):
    def mapping(self, swagger_params):
        import json

        cmd_params = {}
        for k, v in swagger_params.items():
            _, _, arg_idx = CfgReader.find_arg_in_arg_groups_by_name(self.arg_groups, k)
            if not arg_idx or arg_idx in cmd_params:
                continue

            cmd_params[arg_idx] = json.dumps(v)

        return cmd_params

    # def iter_swagger_params(self, swagger_params):
    #     for k, v in swagger_params.items():
    #         yield k, v
    #         if isinstance(v, dict):
    #             for k1, v1 in self.iter_swagger_params(v):
    #                 yield k1, v1
