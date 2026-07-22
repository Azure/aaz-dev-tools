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


def _ssl_ref_args():
    from command.model.configuration._arg import CMDStringArg, CMDObjectArgBase, CMDArrayArg
    inner_id = CMDStringArg({"var": "$parameters.properties.sslCertificates[].id",
                             "options": ["cert-id"], "hide": True})
    inner_pwd = CMDStringArg({"var": "$parameters.properties.sslCertificates[].properties.password",
                              "options": ["cert-password"]})
    elem = CMDObjectArgBase({"args": [inner_id, inner_pwd]})
    arr = CMDArrayArg({"var": "$parameters.properties.sslCertificates",
                       "options": ["ssl-certs"], "item": elem})
    top = CMDStringArg({"var": "$parameters.location", "options": ["l", "location"]})
    return [arr, top]


def _collect_vars(node, out):
    var = getattr(node, "var", None)
    if var:
        out[var] = node
    for sub in (getattr(node, "args", None) or []):
        _collect_vars(sub, out)
    item = getattr(node, "item", None)
    if item is not None:
        _collect_vars(item, out)


def test_remap_arg_var_root_rewrites_nested_vars_and_preserves_customizations():
    ref_args = _ssl_ref_args()
    for arg in ref_args:
        CMDCommand._remap_arg_var_root(arg, "$parameters", "$resource")
    collected = {}
    for arg in ref_args:
        _collect_vars(arg, collected)
    assert set(collected) == {
        "$resource.properties.sslCertificates",
        "$resource.properties.sslCertificates[].id",
        "$resource.properties.sslCertificates[].properties.password",
        "$resource.location",
    }
    # hide/options survive the remap so the current generator can inherit them.
    assert collected["$resource.properties.sslCertificates[].id"].hide is True
    assert collected["$resource.properties.sslCertificates[].properties.password"].options == ["cert-password"]


class _BodyRootCommand(CMDCommand):
    def __init__(self, body_root):
        self._body_root = body_root

    def _detect_body_arg_root(self):
        return self._body_root


def test_remap_ref_args_clones_and_rewrites_body_root():
    ref_args = _ssl_ref_args()
    cmd = _BodyRootCommand("$resource")
    remapped = cmd._remap_ref_args_to_body_root(ref_args)
    # original reference args are not mutated (clone) ...
    orig = {}
    for arg in ref_args:
        _collect_vars(arg, orig)
    assert all(v.startswith("$parameters") for v in orig)
    # ... and the returned args are rewritten onto the current body root.
    remapped_vars = {}
    for arg in remapped:
        _collect_vars(arg, remapped_vars)
    assert "$resource.properties.sslCertificates[].id" in remapped_vars
    assert remapped_vars["$resource.properties.sslCertificates[].id"].hide is True


def test_remap_ref_args_noop_when_root_matches():
    ref_args = _ssl_ref_args()
    cmd = _BodyRootCommand("$parameters")
    assert cmd._remap_ref_args_to_body_root(ref_args) is ref_args


def test_remap_ref_args_noop_when_no_body_root():
    ref_args = _ssl_ref_args()
    cmd = _BodyRootCommand(None)
    assert cmd._remap_ref_args_to_body_root(ref_args) is ref_args
