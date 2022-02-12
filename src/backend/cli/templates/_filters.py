from jinja2.filters import environmentfilter


@environmentfilter
def camel_case(env, name):
    parts = name.replace('-', ' ').replace('_', ' ').split()
    parts = [p[0].upper() + p[1:] for p in parts if p]
    return "".join(parts)


@environmentfilter
def snake_case(env, name):
    parts = name.replace('-', ' ').replace('_', ' ').split()
    parts = [p.lower() for p in parts if p]
    return "_".join(parts)


custom_filters = {
    "camel_case": camel_case,
    "snake_case": snake_case,
}
