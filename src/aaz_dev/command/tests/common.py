from app.tests.common import ApiTestCase
import json
from command.model.configuration._xml import XMLSerializer


class CommandTestCase(ApiTestCase):
    pass


def workspace_name(suffix, arg_name='ws_name'):
    def decorator(func):
        def wrapper(self, **kwargs):
            name = f"{self.__class__.__name__}_{suffix}"
            kwargs[arg_name] = name
            return func(self, **kwargs)
        return wrapper
    return decorator


def verify_xml(self, value):
    data = value.to_primitive()
    xml_data = XMLSerializer.to_xml(value)
    new_arg = XMLSerializer.from_xml(value.__class__, xml_data)
    new_data = new_arg.to_primitive()
    # print(json.dumps(data, indent=4))
    # print(json.dumps(new_data, indent=4))
    self.assertEqual(new_data, data)
