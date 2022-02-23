
def to_camel_case(name):
    assert isinstance(name, str)
    parts = name.replace('-', ' ').replace('_', ' ').split()
    parts = [p[0].upper() + p[1:] for p in parts if p]
    return "".join(parts)


def to_snack_case(name, separator='_'):
    assert isinstance(name, str)
    parts = name.replace('-', ' ').replace('_', ' ').split()
    parts = [p.lower() for p in parts if p]
    return separator.join(parts)
