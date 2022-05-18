from jinja2.filters import pass_environment
from utils.base64 import b64encode_str
from utils.stage import AAZStageEnum


@pass_environment
def command_group_readme_path(env, names):
    return '/'.join(["", "Commands", *names, 'readme.md'])


@pass_environment
def command_readme_path(env, names):
    return '/'.join(["", "Commands", *names[:-1], f'_{names[-1]}.md'])


@pass_environment
def resource_cfg_path(env, resource):
    return '/'.join(["", "Resources", resource.plane, b64encode_str(resource.id), f"{resource.version}.xml"])


@pass_environment
def stage_label(env, stage, bold=True):
    text = stage
    if stage is None:
        text = AAZStageEnum.Stable
    if bold:
        text = f"**{text}**"
    return text


custom_filters = {
    "command_group_readme_path": command_group_readme_path,
    "command_readme_path": command_readme_path,
    "resource_cfg_path": resource_cfg_path,
    "stage_label": stage_label
}
