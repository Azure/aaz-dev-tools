import re


def to_camel_case(name):
    assert isinstance(name, str)
    parts = name.replace('-', ' ').replace('_', ' ').split()
    parts = [p[0].upper() + p[1:] for p in parts if p]
    return "".join(parts)


def to_snack_case(name, separator='_'):
    assert isinstance(name, str)
    name = re.sub('(.)([A-Z][a-z]+)', r'\1' + separator + r'\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1' + separator + r'\2', name).lower()
    return name.replace('-', separator).replace('_', separator)


def to_variation_name(name):
    """Convert name to snack case an replace special characters by '__'"""
    name = to_snack_case(name)
    name = re.sub(r'[^a-z0-9_]', '__', name)
    return name
