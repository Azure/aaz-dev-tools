.. :changelog:

Release History
===============

2.4.0
++++++
* Support data plane client with dynamic endpoint fetched from a response. (#311)

2.3.0
++++++
* Support data-plane generation. (#307)
* Fix bug in swagger discriminator parse. (#305)

2.2.0
++++++
* Add `aaz-dev swagger export-resources` command. (#302)
* Set `utf-8` encoding for all file open. (#298)

2.1.0
++++++
* Support empty object defined in Swagger specification. (#293)

2.0.0
++++++
* Limit a workspace to one resource provider only. (#290)

1.8.0
++++++
* Support to pass an empty request body when it's required (#286)
* Improve the response time of '/AAZ/Editor/Workspaces' api (#287)
* Ignore non-UTF-8 of aaz json file verification (#288)

1.7.1
++++++
* Fix bug when generate property name with special characters in code (#284)

1.7.0
++++++
* Mark a secret property as not required in response flags (#281)
* Raise error when command tree failed to decode, and support configuration key (#282)

1.6.2
++++++
* Convert int value to float for FloatArg default and blank value (#279)

1.6.1
++++++
* Fix bug when special characters appeared in discrimination value (#275)
* Fix docs link in homepage (#277)

1.6.0
++++++
* Adding `profile_` prefix for azure stack profile in CLI aaz package (#274)

1.5.2
++++++
* Update docs for Command Usage and Testing (#270)
* Fix bugs while command has no arguments (#271)
* Add docs for subcommand generation (#272)

1.5.1
++++++
* Add log information for aaz verification (#268)

1.5.0
++++++
* Add command `aaz-dev command-model verify` to verify aaz metadata (#265)

1.4.0
++++++
* Improve Docs of CLI Generator (#258)
* Improve doc display (#259)
* [Doc] Add note for examples (#260)
* Update generation template for pagination (#261)
* Change the initial extension version to 1.0.0b1 (#263)

1.3.1
++++++
* Rewrite the workspace editor doc (#253)
* Refactor the github page for docs (#254)
* Adjust layout for small screen displays. (#255)
* Update faq.md (#256)

1.3.0
++++++
* Support TimeSchema and TimeArg (#250)
* Support `summary` field for swagger operation (#249)

1.2.1
++++++
* Support x-typespec-name and x-typespec-generated in swagger (#243)

1.2.0
++++++
* Support argument prompt input (#238)
* Setup Github Pages, move content into docs and link docs to Github Pages in aaz-dev-tools (#240)

1.1.1
++++++
* Support x-ms-long-running-operation-options.final-state-schema of swagger (#237)

1.1.0
++++++
* Support x-ms-secret of swagger (#235)
* Add support to parse x-ms-arm-id-details and "arm-id" format in swagger (#234)

1.0.2
++++++
* Support PyPI installation (#230)
* Fix cfg reader response.status_codes string join issue (#228)

1.0.1
++++++
* Fix generated code issue for class arguments (#224)

1.0.0
++++++
* GA release
* Add FAQ for LRO missing response defination (#217)
* Add OpenAPI link for LRO response (#218)
* Flatten properties named property by default only when it has sub properties. (#219)
* Fix bug in classify error format (#220)
* Support title property in swagger definition (#221)

0.20.1
++++++
* String output support ref (#213)

0.20.0
++++++
* Fix incorrect statement when checking for content in --cli-path and --cli-extension-path (#205)
* Fix bug when merge sub resources in aaz (#206)
* Support inherent argument hide property on flatten (#207)
* Fix bug for string type output commands (#209)
* Fix sub command inherit bugs (#211)

0.19.3
++++++
* Support default error format for mgmt-plane API (#202)

0.19.2
++++++
* Support resource id filtered by request path in swagger picker (#198)

0.19.1
++++++
* Add pre_instance_create, post_instance_create, pre_instance_delete, post_instance_delete callbacks (#191)
* When generating subresource commands, set default identifier to 'name' if the element of array<object> contains 'id' and 'name' properties (#192)
* Fix array argument element class type display issue (#193)
* Compact json file in aaz output (#194)
* Support 'uri' format in swagger, support 'x-cadl-generated' property in swagger (#195)

0.19.0
++++++
* Feature support subcommand modification inheritance (#184)
* Fix _iter_schema_in_json when js has not schema (#185)
* Update requirements to support Python 3.11 (#186)
* Inherent subresource commands in aaz when export workspace (#187)
* Support partial commands generation in a module (#189)

0.18.0
++++++
* Relink command after class unwrapped (#182)
* Support unwrap class modification inherit (#181)
* Change portal namespace (#179)

0.17.0
++++++
* Workspace swagger picker supports load default swagger module and resource providers (#175)
* `aaz-dev run`: Add `--swagger-module-path`, "--module", "--resource-provider" to specify single swagger repo for code generation (#175)
* `aaz-dev command-model generate-from-swagger`: Support generate command model from swagger by readme tag for pipeline use (#176)
* `aaz-dev cli generate-by-swagger-tag`: Support generate code in cli from command models by using readme tag for pipeline use (#178)
* `aaz-dev regenerate`: Support to regenerate aaz commands from command models (#178)
* Fix Workspace display no arguments command error (#177)
* Ignore '/' character in x-ms-identifiers swagger property (#174)

0.16.2
++++++
* Fix subresource selector in generic update operation (#172)

0.16.1
++++++
* Ignore argument id-parts when generate code for list commands (#169)
* Optimize swagger `Error response` invalid hints (#170)

0.16.0
++++++
* Support build-in keywords in property name generation (#167)
* Add portal CLI generator (#153)
* Support to generate property name starts with digit (#166)
* Support to modify default for array, dict and object arguments (#165)
* Fix `id_part` setup (#164)
* Disable `id_part` for create command and subcommand (#163)
* Support array index auto generate (#162)
* Support to modify argument options for subcommand (#161)
* Support subcommand generation (#154)
* Add FAQs for Swagger definition (#160)
* Fix `x-ms-skip-url-encoding` unparsed in Swagger (#159)

0.15.1
++++++
* Fix `workspace` bug on class argument unwrap (#155)
* Fix `workspace` reload issue for update command using patch (#156)
* Optimize `generation` error message display when loading modules (#157)

0.15.0
++++++
* Fix workspace export to aaz issue. (#148)
* Ignore empty confirmation string in generated code (#149)
* Fix version and readiness parse issue in swagger file path (#150)
* Fix class inheritance overwritten issue (#151)

0.14.0
++++++
* Support class type arguments `unwrap` and `flatten` (#145)
* Support resource url filter in swagger picker (#146)

0.13.0
++++++
* Support free from dict for `"additionalProperties":True` swagger definition (#138)
* Support command confirmation prompt modification (#141)
* Fix duplicated option names detect when flatten argument (#142)
* Fix reload swagger aug group name overwrite (#143)

0.12.0
++++++
* Disable Read only inherent in swagger translators (#139)
* Enable register_callback decorator (#129)

0.11.2
++++++
* Fix cls argument base inherent (#136)
* Fix reload swagger error if no arg change previously (#135)
* Add delete confirmation for workspace delete (#134)

0.11.1
++++++
* Fix patch only not work in workspace editors (#132)
* Fix UI bugs in CLI generators (#132)
* Fix swagger frozen issue in additional properties (#130)

0.11.0
++++++
* Support export unregistered command code (#126)
* Refactor CLI Generators (#126)
* Support lifecycle callbacks in generated AAZCommand code (#127)

0.10.3
++++++
* Support workspace rename and delete (#123)
* Fix resource folder name 255 length limitation (#124)

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
