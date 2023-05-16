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
 