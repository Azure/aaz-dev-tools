from command.model.configuration._command import CMDCommand


class _FakeArg:
    def __init__(self, options):
        self.options = options


def test_body_root_remap_applies_across_generator_roots():
    # TypeSpec generates body args under "$resource.*"; the inherited customizations come from a
    # Swagger cfg keyed under "$parameters.*". The remap must re-apply them; Path args are untouched.
    arguments = {
        "$Path.applicationGatewayName": _FakeArg(["gateway-name"]),
        "$resource.properties.sslCertificates[].name": _FakeArg(["ssl-certificate-name"]),
        "$resource.properties.sslCertificates[].properties.password": _FakeArg(["password"]),
        "$resource.properties.sslCertificates[].id": _FakeArg(["id"]),
    }
    ref_options = {
        "$Path.applicationGatewayName": ["gateway-name"],
        "$parameters.properties.sslCertificates[].name": ["n", "name"],
        "$parameters.properties.sslCertificates[].properties.password": ["cert-password"],
        "$parameters.properties.sslCertificates[].id": ["cert-id"],
    }
    CMDCommand._apply_ref_options_with_body_root_remap(arguments, ref_options)
    assert arguments["$resource.properties.sslCertificates[].name"].options == ["n", "name"]
    assert arguments["$resource.properties.sslCertificates[].properties.password"].options == ["cert-password"]
    assert arguments["$resource.properties.sslCertificates[].id"].options == ["cert-id"]
    # Path arg root is stable, so it is left as-is (already inherited via exact match earlier).
    assert arguments["$Path.applicationGatewayName"].options == ["gateway-name"]


def test_body_root_remap_noop_when_root_matches():
    arguments = {"$resource.foo": _FakeArg(["foo"])}
    CMDCommand._apply_ref_options_with_body_root_remap(arguments, {"$resource.foo": ["bar"]})
    # exact-var match is handled inline in generate_args, not here; same-root keys are skipped.
    assert arguments["$resource.foo"].options == ["foo"]


def test_body_root_remap_skips_ambiguous_multiple_body_roots():
    arguments = {"$a.x": _FakeArg(["x"]), "$b.y": _FakeArg(["y"])}
    CMDCommand._apply_ref_options_with_body_root_remap(arguments, {"$parameters.x": ["X"]})
    assert arguments["$a.x"].options == ["x"]
    assert arguments["$b.y"].options == ["y"]
