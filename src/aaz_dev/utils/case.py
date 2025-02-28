import re
from pluralizer import Pluralizer

_pluralizer = Pluralizer()

def to_camel_case(name, delimeters=""):
    assert isinstance(name, str)
    parts = name.replace('-', ' ').replace('_', ' ').split()
    parts = [p[0].upper() + p[1:] for p in parts if p]
    return delimeters.join(parts)


def to_snake_case(name, separator='_'):
    assert isinstance(name, str)
    name = re.sub('(.)([A-Z][a-z]+)', r'\1' + separator + r'\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1' + separator + r'\2', name).lower()
    return name.replace('-', separator).replace('_', separator)

def to_singular(name):
    return _pluralizer.singular(name)
