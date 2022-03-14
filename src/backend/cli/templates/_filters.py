from jinja2.filters import environmentfilter
from utils.stage import AAZStageEnum
from utils.case import to_camel_case, to_snack_case
import json


@environmentfilter
def camel_case(env, name):
    return to_camel_case(name)


@environmentfilter
def snake_case(env, name):
    return to_snack_case(name)


@environmentfilter
def is_experimental(env, stage):
    return stage == AAZStageEnum.Experimental


@environmentfilter
def is_preview(env, stage):
    return stage == AAZStageEnum.Preview


@environmentfilter
def is_stable(env, stage):
    return stage == AAZStageEnum.Stable


@environmentfilter
def constant_convert(env, data):
    if isinstance(data, str):
        return f'"%s"' % data.replace('"', '\\"')
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


custom_filters = {
    "camel_case": camel_case,
    "snake_case": snake_case,
    "is_experimental": is_experimental,
    "is_preview": is_preview,
    "is_stable": is_stable,
    "constant_convert": constant_convert,
}
