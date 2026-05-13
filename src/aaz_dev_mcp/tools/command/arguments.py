"""Argument-editing tools (patch / flatten / unflatten)."""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def update_argument(
        name: str,
        command: list[str],
        arg_var: str,
        options: Optional[list[str]] = None,
        singular_options: Optional[list[str]] = None,
        help: Optional[dict] = None,
        stage: Optional[str] = None,
        hide: Optional[bool] = None,
        group: Optional[str] = None,
        clear_group: bool = False,
    ) -> dict:
        """Patch a single argument on a leaf command.

        Use this to add aliases (e.g. expose --budget-name also as --name / -n)
        or to tweak help / stage / group.

        - name: workspace name
        - command: full command path without the 'aaz' root, e.g.
          ['consumption', 'budget', 'create']
        - arg_var: argument variable, e.g. '$Path.budgetName'
        - options: replace the argument's option list, e.g.
          ['name', 'n', 'budget-name'] (the first option becomes the
          primary --name; subsequent become aliases)
        - singular_options: alternative singular form for array / cls args
        - help: {'short': str, 'lines': [str], 'refCommands': [str]}
        - stage: 'Stable' | 'Preview' | 'Experimental'
        - hide: bool (cannot hide required args)
        - group: arg group name (non-empty); to remove from a group,
          use ``clear_group=True`` instead of passing an empty string.
        - clear_group: if True, ungroup the argument (places it in the
          default un-named group). Takes precedence over ``group``.
        """
        from ...services.command import arguments
        return arguments.update_argument(
            name=name, command=command, arg_var=arg_var,
            options=options, singular_options=singular_options,
            help=help, stage=stage, hide=hide, group=group,
            clear_group=clear_group)

    @mcp.tool()
    def flatten_argument(
        name: str,
        command: list[str],
        arg_var: str,
        sub_args_options: Optional[dict[str, list[str]]] = None,
    ) -> dict:
        """Flatten an object argument into its sub-arguments.

        Example: flatten '$parameters.properties.timePeriod' on
        'consumption budget create' so users get --start-date / --end-date
        directly instead of having to pass --time-period as a JSON object.

        - name: workspace name
        - command: full command path without the 'aaz' root
        - arg_var: object argument variable to flatten
        - sub_args_options: optional rename map, e.g.
          {'$parameters.properties.timePeriod.startDate': ['start-date']}
        """
        from ...services.command import arguments
        return arguments.flatten_argument(
            name=name, command=command, arg_var=arg_var,
            sub_args_options=sub_args_options)

    @mcp.tool()
    def unflatten_argument(
        name: str,
        command: list[str],
        arg_var: str,
        options: list[str],
        help: dict,
        sub_args_options: Optional[dict[str, list[str]]] = None,
    ) -> dict:
        """Inverse of flatten_argument: collapse sub-args back into one object arg."""
        from ...services.command import arguments
        return arguments.unflatten_argument(
            name=name, command=command, arg_var=arg_var,
            options=options, help=help, sub_args_options=sub_args_options)
