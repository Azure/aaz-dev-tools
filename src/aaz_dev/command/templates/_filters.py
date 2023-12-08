from jinja2.filters import pass_environment
from utils.base64 import b64encode_str
from utils.stage import AAZStageEnum
from utils.plane import PlaneEnum


@pass_environment
def command_group_readme_path(env, names):
    return '/'.join(["", "Commands", *names, 'readme.md'])


@pass_environment
def command_readme_path(env, names):
    return '/'.join(["", "Commands", *names[:-1], f'_{names[-1]}.md'])


@pass_environment
def resource_cfg_path(env, resource):
    plane = resource.plane
    if plane == PlaneEnum.Mgmt:
        plane_folder = plane
    elif PlaneEnum.is_data_plane(plane):
            scope = PlaneEnum.get_data_plane_scope(plane)
            if not scope:
                raise ValueError(f"Invalid plane: Missing scope in data plane '{plane}'")
            plane_folder = '/'.join([PlaneEnum._Data, scope])
    else:
        raise ValueError(f"Invalid plane: '{plane}'")
    return '/'.join(["", "Resources", plane_folder, b64encode_str(resource.id), f"{resource.version}.xml"])


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
