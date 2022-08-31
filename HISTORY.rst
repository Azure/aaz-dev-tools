.. :changelog:

Release History
===============

0.10.2
++++++
* Add cmd unit test docs (#119)
* Limit empty object for create mutability only (#120)
* Fix argument content refresh issue in worksapce editor (#121)

0.10.1
++++++
* Support to parse swagger resource providers without `microsoft` keywords (#116)
* Support swagger modification reload in workspace (#117)

0.10.0
++++++
* Fix command schema duplicated diff calculation issue (#112)
* Support workspace modification inheritance (#113)
* Disable flatten for argument when the schema has cls definition (#114)
* Optimize command description when generated from swagger (#114)
* Support examples inherit (#114)

0.9.6
+++++
* Support modify argument default value and reverse bool argument expression (#106)
* Add default and blank value validation for argbase and arg(#106)
* Add reformat to verify command model(#106)
* Support default value modification ui(#106)
* Ignore argument default for update actions (#107)
* Add argument to specify workspace path (#108)
* Fix bug to print string with newline (#110)

0.9.5
+++++
* Limit minimal python version to 3.8 (#98)(#99)(#101)
* Fix issue when rename commands in cfg_editor (#100)
* Remove python-Levenshtein reliance (#102)
* Disable paging for long running commands (#103)
* Add provisioning state field verification in wait command generation (#104)

0.9.4
+++++
* Update docs (#94)(#95)(#96)

0.9.3
+++++
* Support `DurationArg`, `DateArg`, `DateTimeArg` and `UuidArg` generation (#90)

0.9.2
+++++
* Support empty object argument (#89)
* Add `CMDIdentityObjectSchemaBas` and `CMDIdentityObjectSchema` schema (#89)
* Support use null to unset object or array type elements in dict or array (#89)

0.9.1
+++++
* Fix wait command generation while get operation contains query or header parameters (#88)

0.9.0
+++++
* Support wait command generation (#86)

0.8.0
+++++
* Support argument validation (#85)

0.7.1
+++++
* Fix parse swagger file path version

0.7.0
+++++
* Improve message display in swagger picker (#83)
* Update MIN_CLI_CORE_VERSION to 2.38.0 (#83)

0.6.2
+++++
* Fix issue in _cmd.py.j2 (#80)
* Fix nullable issue for discriminators (#81)
* Fix frozen issue for additional_props (#81)

0.6.1
+++++
* Disable `singular options` generation for list argument by default (#79)

0.6.0
+++++
* Support singular options for list argument (#78)
* Fix argument long summary generation (#78)

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
