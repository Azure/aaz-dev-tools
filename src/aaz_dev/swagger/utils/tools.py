# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

URL_PARAMETER_PLACEHOLDER = "{}"


def swagger_resource_path_to_resource_id_template(path):
    path_parts = path.split("?", maxsplit=1)
    url_parts = path_parts[0].split("/")
    idx = 2  # ignore to the parameter name in first part of url, such as `/{parameter}` or `/{parameter}/...`
    while idx < len(url_parts):
        if url_parts[idx].startswith("{") and url_parts[idx].endswith("}"):
            url_parts[idx] = URL_PARAMETER_PLACEHOLDER
        idx += 1
    path_parts[0] = "/".join(url_parts)
    return "?".join(path_parts)


def swagger_resource_path_to_resource_id(path):
    path_parts = path.split("?", maxsplit=1)
    url_parts = path_parts[0].split("/")
    idx = 2  # ignore to the parameter name in first part of url, such as `/{parameter}` or `/{parameter}/...`
    while idx < len(url_parts):
        if url_parts[idx].startswith("{") and url_parts[idx].endswith("}"):
            url_parts[idx] = URL_PARAMETER_PLACEHOLDER
        idx += 1
    path_parts[0] = "/".join(url_parts).lower()
    return "?".join(path_parts)
