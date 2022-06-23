.. :changelog:

Release History
===============

0.5.1
+++++
* Fix command name generation with url endwith slash (#75)
* Enable more arg types in command generation (#76)
* Fix left over `set_discriminator` in _cmd.py.j2 template (#77)
* Support `nullable` for elements of list and dict args in `update` commands (#77)

0.5.0
+++++
* Support argument hidden in Workspace Editor.
* Fix body parameter required issue.
* Support to pass a required empty object property.

0.4.0
+++++
* [Breaking Change] Replace *.xml by *.json file in `/Resources` folder of `aaz` repo, keep `*.xml` only for model review.

0.3.0
+++++
* Support similar arguments modification
* Fix swagger parse issue: Support `allOf{$ref}` format reference for polymorphic definition.

0.2.2
+++++
* Support confirmation prompt for delete command;
* Fix ext metadata update;

0.2.1
+++++
* Suppress the style issues for generated code;

0.2.0
+++++
* Support argument flatten in Workspace Editor;
* Optimize error message display;

0.1.2
+++++
* Support `--quiet` argument in aaz-dev run to disable web browser page opening;
* Raise error when port is used by others;

0.1.1
+++++
* Use Jinja version 3.0.3;
* Change minimal required cli-core version to 2.37.0;

0.1.0
+++++
* Initial release;
