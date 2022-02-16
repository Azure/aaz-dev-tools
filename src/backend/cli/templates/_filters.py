from jinja2.filters import environmentfilter
from cli.model.atomic import CLIStageEnum
from utils.case import to_camel_case, to_snack_case


@environmentfilter
def camel_case(env, name):
    return to_camel_case(name)


@environmentfilter
def snake_case(env, name):
    return to_snack_case(name)


@environmentfilter
def is_experimental(env, stage):
    return stage == CLIStageEnum.Experimental


@environmentfilter
def is_preview(env, stage):
    return stage == CLIStageEnum.Preview


@environmentfilter
def is_stable(env, stage):
    return stage == CLIStageEnum.Stable


custom_filters = {
    "camel_case": camel_case,
    "snake_case": snake_case,
    "is_experimental": is_experimental,
    "is_preview": is_preview,
    "is_stable": is_stable
}
