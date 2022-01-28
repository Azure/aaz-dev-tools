import os
import logging
import re

logger = logging.getLogger('backend')


def map_path_2_repo(path):
    path = os.path.normpath(path)
    ems = path.split(os.sep)
    idx = ems.index('specification')
    ems = ems[idx:]
    return '/'.join(['https://github.com/Azure/azure-rest-api-specs/tree/master', *ems])


def camel_case_to_snake_case(name, separator='_'):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1' + separator + r'\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1' + separator + r'\2', name).lower()
    return name


def operation_id_separate(op_id):
    value = op_id.strip()
    value = value.replace('-', '_')
    value = value.replace('.', '_')
    value = value.replace(' ', '')
    parts = value.split('_')
    for idx in range(len(parts)):
        part = parts[idx]
        part = camel_case_to_snake_case(part, separator='_')
        parts[idx] = [p for p in part.split('_') if p]
    return parts


def get_url_path_valid_parts(url_path, rp_name):
    """valid parts of url path is a section of url without subscription, resource group and providers"""
    url_path = url_path.split('?')[0]
    parts = url_path.split("/")

    provider_idx = None
    for idx, part in enumerate(parts):
        if part.lower() == rp_name.lower():
            provider_idx = idx

    if provider_idx is None:
        for idx, part in enumerate(parts):
            if part.lower() == "providers":
                provider_idx = idx + 1

    if provider_idx is not None:
        valid_idx = provider_idx
    else:
        valid_idx = 0
        for idx, part in enumerate(parts):
            if part.lower() == "subscriptions":
                valid_idx = idx + 1
            if part.lower() == "resourcegroups":
                valid_idx = idx + 1

    parts = [part for part in parts[valid_idx:] if part not in ('locations', )]
    return parts
