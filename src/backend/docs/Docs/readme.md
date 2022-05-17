# Introduction to AAZDev
---

_AAZDev is a tool that helps Azure CLI developers generate Atomic CLI commands from REST API Specifications._

## 1 Background
---

### 1.1 What is Azure CLI?

The full name of Azure CLI is Azure command-line interface. It's a set of commands used to create and manage Azure resources.

Below is a common CLI command that will create an azure virtual network.

```bash
az network vnet create --name my-vnet --resource-group my-resource-group
```

Every CLI command consists of 2 parts:
- Command name:
  There are thousands of commands in CLI, which are organized into a tree. Its nodes are command groups, and its leaves are commands.
  ```

      az (root)
       |> network (group)
             |> vnet  (group)
                  |> create (command)
  ```
  We call `network vnet` the command group name and `create` the command operation name.
- Argument:
  CLI user can pass in various types of arguments. In addition to the primitive types, users can also pass object, array and dict. For more information, please review [CLI/Argument](/Docs/cli/argument.md).


There are two repos to maintain Azure CLI commands：
- [Azure CLI](https://github.com/Azure/azure-cli)
- [Azure CLI Extension](https://github.com/Azure/azure-cli-extensions)

## 1.2 What is Swagger(OpenAPI Specification)?

Azure uses swagger to define REST API specifications. Most of swagger files are maintained in the following two repos:
- [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs)
- [azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr)

So the definition of API in swagger is required before using AAZDev tool.

## 1.3 What is Atomic CLI Command?

_An Atomic CLI Command operate on one azure resource without dependencies on other things, such as SDK or other commands._

Azure api is designed to be restful. So usually one Atomic CLI command operates on one API.
 But there is an exception, there are multiple APIs that list the same kind of resource in difference scopes. In that case, one list Atomic command operates on multiple APIs. 

Atomic CLI commands do not depend on the SDK or other commands. This brings several advantages to CLI:
- State of truth:
  An Atomic CLI command has all required information in its model and code, so its current state tells how it works without the influence by the change in SDK or other commands. This feature can be used for breaking change detection or other command analysis tasks. 
- Flexible:
  Atomic CLI commands are decoupled from others commands, so it's easy to add, modify, upgrade and release an Atomic CLI command without influence other commands. And the change can be refined down to the API level instead of SDK level. 

The degree of coupling between commands relay on SDK can be seen from the following PR.
![BumpUpNetworkSDK](/Docs/images/az_cli_bump_up_network_sdk.png)
The SDK packages a batch of APIs, and when one API has new change and is released in a new SDK version,
 we have to test and update the commands that use the whole batch of APIs in SDK instead of the one API we care about.
 Each time we bump up a SDK, hundreds of tests need to rerun in live and their recording files need to be updated, we also need to fix other commands that are broken by new SDK.
 It wasted a lot of time and created a lot of hidden problems. By applying Atomic CLI commands, we can avoid them.

## 2 Overview
---

![Architecture](/Docs/diagrams/out/archutecture/architecture.svg)

AAZDev Tool consists of 4 parts:
- API Translators:
  They are responsible for translating the API specification into a command model. We've implemented the swagger 2.0 translator which can support to translate the API specs in [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repo and [azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr) repo.
- Model Editors:
  They are used to edit command models. Currently _Workspace Editor_ is implemented. More details are introduced in _Workspace_ paragraph.
- Command Models:
  The command models generated from translators and modified in editors will be persisted in a repo called AAZ. The persistence of models can be useful in many ways. More details are introduced in _AAZ Repo_ paragraph.
- Code Generators:
  They are used to generator code from command models. The _CLI Generator_ is implemented to generate code into [Azure CLI](https://github.com/Azure/azure-cli) repo and _CLI Extension Generator_ is for [Azure CLI Extension](https://github.com/Azure/azure-cli-extensions)

For CLI Developers, they edit command models in Model Editors and select command models for Code Generators. 

## 3 Swagger V2 Translator
---

A Resource can be translated into a single command or multiple commands under a command group.

### 3.1 Group part naming

Swagger V2 translator uses the `valid part` of url to generate the group part of a command.

The `valid part` of url is the url suffix starts by it's Resource Provider with parameter placeholders replaced by `{}` and locations segment removed.

The table below show some examples with valid part highlighted.
| Resource Provider | Resource Url | valid part of url |
| ---- | ---- | ---- |
| Microsoft.EdgeOrder | /subscriptions/{subscriptionId}/providers/`Microsoft.EdgeOrder/addresses` | Microsoft.EdgeOrder/addresses |
| Microsoft.EdgeOrder | /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/`Microsoft.EdgeOrder/addresses` | Microsoft.EdgeOrder/addresses |
| Microsoft.EdgeOrder | /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/`Microsoft.EdgeOrder/addresses/{`addressName`}` | Microsoft.EdgeOrder/addresses/{} |
| Microsoft.EdgeOrder | /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/`Microsoft.EdgeOrder`/locations/{location}`/orders/{`orderName`}` | Microsoft.EdgeOrder/orders/{} |
| Microsoft.Network | /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/`Microsoft.Network/virtualNetworks/{`virtualNetworkName`}/subnets/{`subnetName`}` | Microsoft.Network/virtualNetworks/{}/subnets/{} |
| Microsoft.Consumption | /providers/Microsoft.Management/managementGroups/{managementGroupId}/providers/Microsoft.Billing/billingPeriods/{billingPeriodName}/`Microsoft.Consumption/aggregatedcost` | Microsoft.Consumption/aggregatedcost |

Each segments of valid part corresponds to a group name. The parameter segments are ignored by default. And `Microsoft.` prefix in resource provider segment is ignored too. The singular values of the remaining segments are converted to snake case with `-` as separator.
 For example `Microsoft.Network/virtualNetworks/{}/subnets/{}` has three segments: `Microsoft.Network`, `virtualNetworks`, `subnets` and they correspond to `network`, `virtual-network` and `subnet`. So the full command group name will be `network virtual-network subnet`

### 3.2 Operation part naming

Swagger V2 translator use the HTTP methods to generate the operation part of a command.

The table below show the mapping relation ship between the common command operation name and the resource HTTP methods.

| Common Command Operation Name | Resource HTTP Method |
| ---- | ---- |
| show | GET |
| list | GET |
| create | PUT |
| delete | DELETE |
| update (by generic) | GET + PUT |
| update (by patch) | PATCH |

For example if a resource has following properties:

```yaml
resource_id: '/subscriptions/{}/resourcegroups/{}/providers/microsoft.edgeorder/addresses/{}'
methods:
    - GET
    - DELETE
    - PUT
    - PATCH
```

This resource will be translated into four commands under `az edge-order address` command group:

```yaml
az data-bricks workspace:
    - show
    - delete
    - create
    - update
```

The `show`, `delete`, `create` commands call `GET`, `DELETE`, `PUT` methods respectively.

The `update` command will either use a combination of `GET`+`PUT` methods or a single `PATCH` method.
 When all three methods exist in a resource, `Generic First` operation will use `GET`+`PUT` combination, and `Patch First` will use `PATCH` method.

Translators will also detect a `GET` method should be named as `show` or `list` based on its url and response schema.
 For example the following two resources will generate `list` command of `az edge-order address`.

```yaml
resource_id: '/subscriptions/{}/providers/microsoft.edgeorder/addresses'
methods:
    - GET
```

```yaml
resource_id: '/subscriptions/{}/resourcegroups/{}/providers/microsoft.edgeorder/addresses'
methods:
    - GET
```

Translators will automatic merge them into one `list` commands if their response schemas are the same. If their response schemas are different, a special suffix will be added after `list` operation name to distinguish two commands. And the name can be renamed in editor.

The `POST` method is special. If a resource has `POST` method only and the last segment of valid part is not a parameter segment, that segment will be used as operation name, else a temporary name will be generated, which can be renamed in editor later.


## 4 Workspace
---

Before developers finish customizing the command models and export them in AAZ repo for persistence, the draft is saved in a workspace.
Workspaces are like containers, they are isolated so that changes in one do not affect the others. Therefore, developers can create as many workspaces as needed for different purposes. 

It's possible to add resources from different resource providers, but they should be in the same plane. Currently we only support Management plane.
Another note is that a workspace don't allow to add a resource multiple times in different versions. For example, if virtual network resource('/subscriptions/{}/resourcegroups/{}/providers/microsoft.network/virtualnetworks/{}') of version 2021-05-01 is added in a workspace, it's not allowed to add other versions of this resource in this workspace.

Please jump to [Workspace Editor](/Docs/usage/workspace_editor_usage.md) for more details.

## 5 AAZ Repo
---

The name __AAZ__ comes from the abbreviation of Atomic Azure. This repo is to maintain Atomic Azure Cli command models. You can access this repo by [link](https://github.com/kairu-ms/aaz/tree/demo).

There a two folders in the root of AAZ:
- Commands:
  This folder provides an index of command models available in AAZ. They are organized in a command tree. 
- Resources:
  This folder save command models in xml files which is called command configurations. Those files are separated by resources.

### 5.1 Command Tree

The data of command tree is in [Commands/tree.json](https://github.com/kairu-ms/aaz/blob/demo/Commands/tree.json). Json files are hard to read, so the data is also rendered as Markdown files in a tree hierarchy.

![CommandTreeNode](/Docs/images/aaz_command_tree_folder.png)

Each folder represents each node of the tree and also represents a command group. Its readme.md file shows the summery, subgroups and commands of this group. And the links in the file help us to browse quickly.

![CommandTreeLeaf](/Docs/images/aaz_command_tree_command_md.png)

Each Markdown files starts with '_' represents each leaf of the tree which also represents a command. Its contains the summery, versions and examples of this command. And each version links to a command configuration in Resources folder. 

### 5.2 Command Configuration

The format of command configuration file path is:

```
Resources/{plane}/{base64(resource_id)}/{api_version}.xml
```

![CommandConfiguration](/Docs/images/aaz_command_configuration.png)

A command configuration file contains more than one commands, which are generated from the same resource.

The diagram below show the structure of command configuration file.
![CommandConfigurationFileStructure](/Docs/diagrams/out/command_configuration/file_structure.svg)

The commands in a configuration file organized in hierarchy.

There are three sections in every commands:
- Argument Section:
  The arguments defined in argument section and grouped by Argument Group.
- Operation Section:
  The operations performed by the command are defined in Operation Section. Currently, there are two kinds of operations:
    - HTTP Operations: This kind of operations are used to generate HTTP request.
    - Instance Operations: This kind of operations are used to change the data of resource instance.
- Output Section:
  The output transformations are defined in Output Section.
The data flow from Argument Section to Operation Section and then to Output Section. The arguments are linked with operations by their variant name. The operations are generated by swagger and do not support customization.
 The Operation Section in diagram is from a classic `update` command which use `get+put` methods. In model editors the modification of arguments and special output formats are supported.

## 6 CLI Generator and CLI Extension Generator
---

### 6.1 Command Module

CLI commands are separated into different command modules in Azure CLI repo or Azure CLI extension repo. So it's required to select a specific module for generators.

![CommandModules](/Docs/images/az_cli_and_az_cli_extension_command_modules.png)

### 6.2 Profile

Azure CLI uses profiles to support Azure Stack. There are five profiles:
- latest
- 2020-09-01-hybrid
- 2019-03-01-hybrid
- 2018-03-01-hybrid
- 2017-03-09-profile

The `latest` profile contains a full set of commands and the rest profiles contains a sub set of commands from the `latest`.
One command may call different api versions in different profiles. So its arguments and output schema may vary from profile to profile.

Please jump to [CLI Generator](/Docs/usage/cli_generator_usage.md) for more details.
