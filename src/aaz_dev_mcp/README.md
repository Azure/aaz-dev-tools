# aaz-dev-mcp

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes
[aaz-dev-tools](https://github.com/Azure/aaz-dev-tools) workflows as tools an
LLM agent can call. It wraps the same Python controllers the web UI uses, so
generated CLI code is identical to what you'd get by clicking through the
browser.

## Scope (v1)

Reproduce the end-to-end flow of an Azure CLI swagger-version bump PR (e.g.
[azure-cli#33222](https://github.com/Azure/azure-cli/pull/33222)):

1. Configure repo paths.
2. Create or load a workspace.
3. Add swagger resources at a specific API version.
4. (Optional) tweak help text on command groups.
5. Generate to the `aaz` repo.
6. Select per-command versions for an azure-cli module and regenerate Python code.

## Install

This package depends on `aaz-dev-tools` itself being installed in the same
Python environment.

```bash
# from the repo root
python -m venv .venv
source .venv/bin/activate
pip install -e .                # installs aaz-dev-tools controllers
pip install -e src/aaz_dev_mcp  # installs aaz-dev-mcp + MCP SDK
```

## Configuration

The server reads the same environment variables aaz-dev-tools uses:

| Variable | Purpose |
| --- | --- |
| `AAZ_PATH` | clone of `Azure/aaz` |
| `AAZ_SWAGGER_PATH` | clone of `Azure/azure-rest-api-specs` |
| `AAZ_CLI_PATH` | clone of `Azure/azure-cli` |
| `AAZ_CLI_EXTENSION_PATH` | clone of `Azure/azure-cli-extensions` |
| `AAZ_DEV_WORKSPACE_FOLDER` | where workspace ws.json files live (default `~/.aaz_dev/workspaces` — same default as the Flask UI, so workspaces are shared by default) |

You can also override at runtime by calling the `configure` tool first.

## Running

The server speaks MCP over **stdio**:

```bash
aaz-dev-mcp
```

## GitHub Actions issue codegen

This repo also includes a lightweight GitHub Actions flow for issue-driven
codegen. It does not run the MCP stdio server in CI; it calls the shared Python
helpers directly.

1. Create an **AAZ Codegen Request** issue and describe the API version in
   prose, e.g. `Generate Azure CLI for Microsoft.Consumption using API version
   2024-08-01.`
2. The `codegen:request` label triggers `.github/workflows/aaz-codegen-preview.yml`.
   The workflow calls GitHub Models with the built-in `GITHUB_TOKEN`
   (`models: read`) to extract candidate fields, validates them against
   `Azure/azure-rest-api-specs@main`, and comments a preview.
3. Comment `/codegen` on an issue with a valid preview to run
   `.github/workflows/aaz-codegen-run.yml`. The run uses the latest valid bot
   preview, generates into `Azure/aaz` and `Azure/azure-cli`, and opens or
   updates draft PRs.

The `/codegen` workflow never writes to a developer's local checkout. It checks
out fresh copies of `Azure/aaz`, `Azure/azure-cli`, and `Azure/azure-rest-api-specs`
inside the GitHub Actions runner workspace, modifies those runner worktrees,
then pushes bot branches and opens or updates draft PRs.

GitHub Models does not require Azure OpenAI secrets. Cross-repo PR creation
still requires a token that can push branches and open PRs in `Azure/aaz` and
`Azure/azure-cli`; configure it as `CODEGEN_GITHUB_TOKEN`. Without that secret,
the workflow falls back to `GITHUB_TOKEN`, which usually cannot write to those
repos from this control repo.

### Testing the flow from a branch

GitHub issue and issue-comment events are repository events, so they are not a
good way to test a brand-new workflow file that only exists on a feature branch.
Use `.github/workflows/aaz-codegen-branch-test.yml` for pre-merge smoke tests.

Push a commit whose message contains `[aaz-codegen-test]` to run the GitHub
Models extraction and preview validation against a synthetic issue. Use
`[aaz-codegen-run-test]` to also run deterministic codegen against fresh runner
checkouts of `Azure/aaz` and `Azure/azure-cli`.

To test draft PR creation before merging the issue workflow, configure
`CODEGEN_GITHUB_TOKEN`, then push a commit whose message contains
`[aaz-codegen-pr-test]`. That mode still uses fresh runner checkouts, but it
also pushes generated branches to `Azure/aaz` and `Azure/azure-cli` and opens
draft PRs. It never comments on GitHub issues.

### Claude Desktop / OpenCode config snippet

```json
{
  "mcpServers": {
    "aaz-dev": {
      "command": "/absolute/path/to/.venv/bin/aaz-dev-mcp",
      "env": {
        "AAZ_PATH": "/Users/you/workspaces/aaz",
        "AAZ_SWAGGER_PATH": "/Users/you/workspaces/azure-rest-api-specs",
        "AAZ_CLI_PATH": "/Users/you/workspaces/azure-cli",
        "AAZ_CLI_EXTENSION_PATH": "/Users/you/workspaces/azure-cli-extensions"
      }
    }
  }
}
```

## Sharing workspaces with the Flask UI

Workspaces are not MCP-specific. Both the MCP server and the Flask UI in
`aaz-dev` go through the same `WorkspaceManager`, which stores each
workspace as `<AAZ_DEV_WORKSPACE_FOLDER>/<name>/{ws.json, Resources/...}`
on disk.

If both processes use the same `AAZ_DEV_WORKSPACE_FOLDER` (the default
`~/.aaz_dev/workspaces` for both), an MCP-created workspace shows up in
the UI's workspace list automatically and you can edit its command tree,
arguments, examples, etc., in the browser. Likewise, the MCP can `load`
and modify workspaces that were created in the UI.

A few things to keep in mind:

- **No IPC** — if you have the UI open while the MCP writes the same
  workspace (or vice versa), the UI's in-memory copy is stale. Refresh.
- **Optimistic concurrency** — `WorkspaceManager.save()` compares a
  `ws.version` UTC timestamp against the on-disk copy
  (`workspace_manager.py:213`). Concurrent saves to the same workspace
  fail with `ResourceConflict("Workspace Changed after: ...")` rather
  than corrupting state. Re-load and retry.
- **Other paths must also match** — if the UI's `AAZ_PATH` /
  `AAZ_CLI_PATH` / etc. point at different checkouts than the MCP's,
  `generate_to_aaz` and `update_*_module` from each side write to
  different repos. Keep them aligned (or be intentional about the split,
  e.g. UI -> real repos, MCP -> worktrees).

## Tools

| Tool | Purpose |
| --- | --- |
| `configure` | Set/inspect paths to aaz, swagger, cli, extensions, workspace folder. |
| `list_workspaces` | List ws.json folders under the configured workspace folder. |
| `create_workspace` | Create a new workspace. Errors if it already exists. |
| `load_workspace` | Load an existing workspace's command tree. |
| `add_swagger_resources` | Add ARM resource paths at a given API version into the workspace. |
| `set_node_help` | Update help text / stage on a command-group node. |
| `set_command_help` | Update help text / stage on a leaf command. |
| `rename_command_group` | Rename or re-parent a command-group node, e.g. `node_names=["consumption","usage-detail"]` → `new_node_names=["consumption","usage"]`. |
| `rename_command` | Rename or re-parent a leaf command, e.g. `leaf_names=["consumption","pricesheet","default","show"]` → `new_leaf_names=["consumption","pricesheet","show"]`. |
| `update_argument` | Patch a single argument on a leaf (options/help/stage/hide/group/singular_options). Use to add aliases like `--name`/`-n` to `--budget-name`. Pass `clear_group=True` to ungroup an arg. |
| `flatten_argument` | Flatten an object argument into its sub-arguments (e.g. `--time-period` → `--start-date` + `--end-date`). |
| `unflatten_argument` | Inverse of `flatten_argument`. |
| `list_command_examples` | Read the current examples on a leaf command. |
| `add_command_example` | Append a single manual `{name, commands}` example (mirrors the editor's "Add Example" dialog). |
| `add_examples_from_swagger` | Generate examples from the OpenAPI spec (the editor's "By OpenAPI Specification" button) and persist them; supports `replace=False/True`. |
| `set_command_examples` | Replace the full example list on a leaf (pass `[]` to clear). |
| `generate_to_aaz` | Export the workspace command tree to the `aaz` repo. |
| `get_main_module` / `get_extension_module` | Read the current CLI profile for an azure-cli or extensions module. |
| `update_main_module` / `update_extension_module` | Generate CLI code from a full profiles dict. Accepts `by_patch` (default `true`). |
| `select_command_versions` | High-level: pick `{command: version}` and generate. Accepts `by_patch` (default `true`). |

## Typical workflow

1. `configure(...)` (or rely on env vars)
2. `create_workspace(name="consumption-2024-08-01", mod_names="consumption", resource_provider="Microsoft.Consumption")`
3. `add_swagger_resources(name=..., module="consumption", version="2024-08-01", resource_paths=[...])`
4. `rename_command_group(name=..., node_names=["consumption","usage-detail"], new_node_names=["consumption","usage"])` (and similar for `reservation-summary` → `reservation summary`, `reservation-detail` → `reservation detail`; `rename_command` for `pricesheet default show` → `pricesheet show`).
5. `set_node_help(name=..., node_names=["consumption","budget"], help={"short": "Manage consumption budgets."})` (optional)
6. `generate_to_aaz(name=...)`
7. `select_command_versions(target="main", module_name="consumption", by_patch=False, command_versions={"consumption budget create": "2024-08-01", ...})`

### `by_patch` semantics

`by_patch` (passed to `update_*_module` / `select_command_versions`) only
controls whether unmodified commands re-read their existing config files.
It does **not** preserve commands that are absent from the input profile —
codegen always rewrites the entire `aaz/latest/` tree.

If you are introducing brand-new leaves (e.g. `consumption usage list`,
`consumption reservation summary list`) that don't yet exist in the CLI
module, you must pass `by_patch=False`. Otherwise the profile generator
hits `AssertionError: command.cfg is not None`
(`az_profile_generator.py:103`).

## Notes

- Each tool catches `ValueError` from `Config` setters and returns it as a
  structured error.
- Errors raised by controllers (`exceptions.ResourceConflict`,
  `exceptions.InvalidAPIUsage`, etc.) propagate as MCP tool errors.
- Workspaces use optimistic concurrency: a `ws.version` timestamp is checked
  on every save. If you run the Flask dev server and the MCP simultaneously
  and both write the same workspace, the second writer will error.
