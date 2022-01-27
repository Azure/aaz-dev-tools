from aazdev.tests.common import ApiTestCase


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
