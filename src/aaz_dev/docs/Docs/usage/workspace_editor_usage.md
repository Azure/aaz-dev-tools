# Introduction to Workspace Editor
---
![Architecture](/Docs/diagrams/out/archutecture/architecture.svg)
As shown from the overview diagram above, workspace is used to store and edit various customerized command models. Normally, its path is `/Users/yourname/.aaz/workspaces` where all the historical command models' workspace you created are located.
## Workspace Editor Usage
---
When a new set of CLI commands needs to be generated using AAZDev Tool, [workspace editor](#/Workspace) page is the starting point. 
### 1. Set Workspace
Developers can select an existed workspace from the drop-down menu or create a new workspace by typing in a nonexistent name. 
![workspace](/Docs/images/workspace.png)

### 2. Add Resource
After determing the workspace, target resource can be searched and added by filtering swagger modules and API version. As noted before, a resource cannot be added into the same workspace multiple times in different api versions.
![add_resource](/Docs/images/add_resource.png)

### 3. Modify Command Model
According to previous [intro](#/Documents), swagger translator will generate a set of commands from chosen resource with its group and operation parting naming protocol. In the popped command tree, we can: 
  
  a. rename command group

  By clicking and editing the command group name, developer can adjust the swagger-translated long command name into a less redundant version, like: `az network managmentt security-user-configuration` -> `az network mgmt suc`. Also, in the corresponding editing window, short summary can be added as required.
  ![group_edit](/Docs/images/group_edit.png)
  ![group_edit1](/Docs/images/group_edit1.png)

  b. adjust command

  Click into a command and developers can use the upper `edit` button to do some modifications and add short help message and use the bottom `add` button to add command examples for usage. 

  `Delete` button can be used if current command is no longer needed and needs to be deleted. Meanwhile the corresponding command group can only be deleted when all the children command are deleted. 

  ![command_edit](/Docs/images/command_edit.png)


  c. adjust argument
  
  By clicking into an argument under a command, the popped up window can be used to:a) add optional argument names seperated by space; b) change the argument groups for better argument management and display; c) add short summary as argument help message. d) flatten an argument
  if this argument has only one prop, a more condense argument can be generated using argument `flatten` and the previous argument `arg1` will be named into `arg1-prop` under a seperate `arg1 Group` argument group.
  ![argument_edit](/Docs/images/argument_edit.png)
  

  d. adjust stages
  
  As is known in the popped command and argument windows, there are three stages shown: Stable, Preview and Experimental. Detailed infos and support levels can be found in this [link](https://docs.microsoft.com/en-us/cli/azure/reference-types-and-status#what-is-reference-status) where GA(Generally Available) means Stable in workspace editor. A preview or experimental command/argument can be change into a Stable version or be removed in later release as short-time functional testing while a stable one cannot be chaned into the other status or deletd. 

### 4. Export Command Repos
After all modificationa for command groups, arguments, developer can export current command workspace into your previously folked and cloned AAZ repo using top-right `Export` button, whose path would be `path/to/your/cloned/aaz`. AAZ repo is to maintain all public Atomic Azure Cli command models.
![export](/Docs/images/export.png)
