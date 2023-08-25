from jinja2.filters import pass_environment
from utils.stage import AAZStageEnum
from utils.case import to_camel_case, to_snake_case
import re


@pass_environment
def camel_case(env, name):
    return to_camel_case(name)


@pass_environment
def snake_case(env, name):
    return to_snake_case(name)


@pass_environment
def is_experimental(env, stage):
    return stage == AAZStageEnum.Experimental


@pass_environment
def is_preview(env, stage):
    return stage == AAZStageEnum.Preview


@pass_environment
def is_stable(env, stage):
    return stage == AAZStageEnum.Stable


@pass_environment
def constant_convert(env, data):
    if isinstance(data, str):
        return f'"%s"' % data.replace('"', '\\"').replace('\n', '\\n')
    elif isinstance(data, (int, float, bool)):
        return f"{data}"
    elif data is None:
        return f"None"
    elif isinstance(data, list):
        return '[%s]' % ', '.join(constant_convert(env, x) for x in data)
    elif isinstance(data, dict):
        return '{%s}' % ', '.join(
            ': '.join([constant_convert(env, k), constant_convert(env, v)])
            for k, v in data.items()
        )
    else:
        raise NotImplementedError()


_PYTHON_BUILD_IN_KEYWORDS = (
    'False', 'await', 'else', 'import', 'pass', 'None', 'break', 'except', 'in', 'raise', 'True', 'class', 'finally',
    'is', 'return', 'and', 'continue', 'for', 'lambda', 'try', 'as', 'def', 'from', 'nonlocal', 'while', 'assert',
    'del', 'global', 'not', 'with', 'async', 'elif', 'if', 'or', 'yield'
)


@pass_environment
def get_prop(env, data):
    assert isinstance(data, str)
    if not re.match('^[A-Za-z_][A-Za-z0-9_]*$', data) or data in _PYTHON_BUILD_IN_KEYWORDS:
        # including property name starts with digit like `0ab`
        # including property name special character such as `odata.type`
        # including python build in keywords
        return f'[{constant_convert(env, data)}]'
    else:
        return f'.{data}'


custom_filters = {
    "camel_case": camel_case,
    "snake_case": snake_case,
    "is_experimental": is_experimental,
    "is_preview": is_preview,
    "is_stable": is_stable,
    "constant_convert": constant_convert,
    "get_prop": get_prop
}
