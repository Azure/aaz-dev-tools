"""Command-example tools (list / add / generate-from-swagger / set)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def list_command_examples(name: str, command: list[str]) -> list[dict]:
        """Return the current examples on a leaf command.

        - name: workspace name
        - command: full command path without the 'aaz' root
        """
        from ...services.command import examples
        return examples.list_command_examples(name=name, command=command)

    @mcp.tool()
    def add_command_example(
        name: str,
        command: list[str],
        example_name: str,
        commands: list[str],
    ) -> list[dict]:
        """Append a single manually-authored example to a leaf command.

        Mirrors typing in the editor's "Add Example" dialog.

        - name: workspace name
        - command: full command path without the 'aaz' root, e.g.
          ['consumption', 'budget', 'create']
        - example_name: short label shown in CLI help
        - commands: list of CLI invocation strings, e.g.
          ['consumption budget create -n my-budget --amount 100 --category Cost ...']

        Returns the full updated example list.
        """
        from ...services.command import examples
        return examples.add_command_example(
            name=name, command=command,
            example_name=example_name, commands=commands)

    @mcp.tool()
    def add_examples_from_swagger(
        name: str,
        command: list[str],
        replace: bool = False,
    ) -> list[dict]:
        """Generate examples from the OpenAPI spec (the editor's
        'By OpenAPI Specification' button) and persist them on the leaf.

        - replace=False (default): append generated examples to existing ones.
        - replace=True: drop existing examples first.

        Returns the full updated example list.
        """
        from ...services.command import examples
        return examples.add_examples_from_swagger(
            name=name, command=command, replace=replace)

    @mcp.tool()
    def set_command_examples(
        name: str,
        command: list[str],
        examples: list[dict],
    ) -> list[dict]:
        """Replace all examples on a leaf command. Each example is
        ``{"name": str, "commands": [str, ...]}``. Pass [] to clear."""
        from ...services.command import examples as cmd_examples
        return cmd_examples.set_command_examples(
            name=name, command=command, examples=examples)
