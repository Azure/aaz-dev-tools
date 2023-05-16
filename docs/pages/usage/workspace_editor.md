---
layout: page
title: Workspace Editor
permalink: /usage/workspace-editor/
weight: 101
---

# Introduction to Workspace Editor

![Architecture](../../assets/diagrams/out/archutecture/architecture.svg)

Workspaces are used to save and edit command models before exporting them to `aaz` repo. They are isolated with each other. So you can create multiple workspaces for different purpose. And they are saved in `~/.aaz/workspaces` folder by default.

## Workspace Editor Usage

When using aaz-dev from stratch, the workspace editor is the starting point. 

### Workspace operations

#### Create a workspace

In workspace page, the drop-dowm menu can select an existing workspace or create a new one.

![create_a_workspace](../../assets/recordings/workspace_editor/create_a_workspace.gif)

#### Rename a workspace

Click the `EDIT` button you can rename the opened workspace.

![rename_a_workspace](../../assets/recordings/workspace_editor/rename_a_workspace.gif)

#### Delete a workspace

Click the `DELETE` button you can delete the opened workspace. It requires to input workspace name again to confirm.

> **Warning**
> aaz-dev does not support __Undo__. Once the workspace is deleted you cannot get it back unless you use `git` to manage the workspaces folder (default path is `~/.aaz/workspaces`).

![delete_a_workspace](../../assets/recordings/workspace_editor/delete_a_workspace.gif)

### Add Swagger Resources

When an empty workspace is opened, the `Add Swagger Resources` page will be prompted out by default.

For a workspace contains commands, click the `+` button besides the `command tree`, the `Add Swagger Resources` page will prompted out as well.

![prompt_add_swagger_resources_page](../../assets/recordings/workspace_editor/prompt_add_swagger_resources_page.gif)

#### Swagger Filters

The Swagger Filters can help you quickly filter out the resources to generate commands. They are

- Swagger Module selector
- Resource Provider selector
- API Version selector

![filter_swagger_resources](../../assets/recordings/workspace_editor/filter_swagger_resources.gif)

#### Pick Resource Urls

After the resources are filtered, you can select the resource urls on the right table.

> **Note**
> For the resources already added in the current workspace, their urls will be filtered out in the table. That's by design to avoid you add the same resource multiple times in one workspace, even in different api-versions is not allowed.

You can select them `All` or only pick some of them on demand which is recommended for beginners. You can also use the `Filter` bar to filter out a table by some keywords or the path key in swagger.

Click `Submit` button will generate command models in workspace and back to the workspace page. Those new commands are added in the command tree.

![pick_resource_urls](../../assets/recordings/workspace_editor/pick_resource_urls.gif)

#### Inherit modifications from exported command models

While adding a swagger resource, aaz-dev supports to inherit modifications directly from command models of the same resource generated and exported in `aaz` repo. This avoids many repetitive works. You can select different versions to inherit.

![pick_resources_with_inheritance](../../assets/recordings/workspace_editor/pick_resources_with_inheritance.gif)

#### The generation of `Update` commands

There are two mechanisms to implement `Update` in azure-cli.

- Generic Update: use `Get` request to fetch the resource, modify the resource and use `Put` request to submit the whole modified resource. About __99%__ `Update` commands in azure-cli use this mechanism.
- Patch Update: use `Patch` request to submit the change only.

There's three modes to control the generation of `Update` commands while add the resources.

- Generic(Get&Put) First: If the resource supports `Get` and `Put` methods, generate the _Generic Update_, else if it supports `Patch` method, it generate the _Patch Update_.
- Patch First: If the resource supports `Patch` method, it generate the _Patch Update_, else if it supports `Get` and `Put` methods.
- No update command: Never generate `Update` commands for the resource.

> **Note**
> This selection will apply to all the resources to submit. So if some of the resources should use a different mode, you should pick and submit them in the next new `Add Swagger Resources` page with a different mode.

![pick_resources_with_update_modes](../../assets/recordings/workspace_editor/pick_resources_with_update_modes.gif)

#### Issues while adding swagger

The aaz-dev tool uses strict mode to parse swagger. It will cause problems when adding swagger resources if the swagger files contains non-standard definitions. If you encounter such problem, you should check the __logs__ of aaz-dev __backend service__ and create a github issue in aaz-dev-tools repo or post it in _Team Channel_: `Azure CLIs partners/Azure CLI CodeGen`

![pick_resource_with_issues](../../assets/recordings/workspace_editor/pick_resource_with_issues.gif)
