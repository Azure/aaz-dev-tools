# CLI Generator Usage
---
## Command Generation
---
### 1. Choose Command Model
CLI commands are separated into different command models in Azure CLI repo or Azure CLI extension repo. Before generate CLI command, select the target command module.
![model_select](/Docs/images/module_select.png)
### 2. Generate Commands
In the commands display page, check the commands exported from [model editor](#/Workspace), and select the target api version, then click the top-right `Generate` buttton. CLI command code generated from AAZ Development Tool has been added into your cloned local azure-cli directory for further debugging and testing. 
![code_gen](/Docs/images/code_gen.png)

## About
---
### Azure CLI vs Azure CLI Extension

#### CLI Modules

|                                   PROS                                  |                                                                             CONS                                                                             |
|:-----------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| Comes automatically with the CLI. No dedicated installation required.   | Strictly tied to CLI release schedule                                                                                                                        |
| Unlikely to be broken by changes to azure-cli-core (with test coverage) | STRICTLY tied to CLI authoring guidelines. Experimental patterns that may be allowed in extensions could be rejected entirely for inclusion as a CLI module. |

#### Extensions

|                      PROS                      |                         CONS                         |
|:----------------------------------------------:|:----------------------------------------------------:|
| Release separate from the CLI release schedule | Requires dedicated installation (az extension add …) |
| Higher velocity fixes possible                 | Can be broken by changes to the azure-cli-core       |
| Experimental UX is permissible                 |                                                      |
| Leverage CLI code generator to generate code   |                                                      |


- Common uses for extensions include experimental commands, commands in private or public preview, or to separate between frequently used and rarely used functionality (where infrequently used commands are acquired via extension).
- Note that if you are trying to get commands into the CLI out of step with the normal release cycle, extensions are your **only** option.
- Because non-standard, experimental authoring patterns are permitted for extensions, simply trying to "move an extension into the CLI" is often **not** a trivial process and will necessitate a full review with higher scrutiny from the CLI team. Expect to need to make changes.
- For more details about CLI vs CLI extension, please check [here](https://github.com/Azure/azure-cli/blob/dev/doc/onboarding_guide.md#extension-vs-module)
- In this editor, only CLI commands are generated. For advanced CLI extension generation techniques, please check [here](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/authoring.md)


### Profile
The Azure CLI supports multiple profiles. Help can be authored to take advantage of this.  
Commands available, arguments, descriptions and examples all change dynamically based on the profile in use.

The `az cloud update --profile ...` command allows you to switch profiles.  
You can see an example of this by switching profiles and running `az storage account create --help`.

For more info, please check [here](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_help.md#profile-specific-help)
