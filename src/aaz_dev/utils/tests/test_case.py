import ast

from utils.case import to_snake_case, to_camel_case


def test_to_snake_case_strips_angle_brackets():
    # aaz-dev-tools#562: generic type names carry angle brackets that must not leak into identifiers.
    result = to_snake_case("Record<UserAssignedIdentityResourceId>")
    assert "<" not in result and ">" not in result
    # the produced attribute/method name must be a valid Python identifier
    ast.parse(f"_args_{result} = None")


def test_generic_cls_name_produces_valid_identifier():
    # mirrors the code generator: cls name -> "_args_" + snake_case must be assignable Python.
    cls_name = to_camel_case("Record<UserAssignedIdentityResourceId>") + "_CreateOrUpdate_create"
    for prefix in ("_args_", "_build_args_", "_schema_", "_build_schema_"):
        ast.parse(f"{prefix}{to_snake_case(cls_name)} = None")
