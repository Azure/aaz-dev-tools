import * as React from "react";
import { Box, Dialog, Slide, Drawer, Toolbar } from "@mui/material";
import { useParams } from "react-router";
import { TransitionProps } from "@mui/material/transitions";
import WSEditorSwaggerPicker from "../WSEditorSwaggerPicker";
import WSEditorToolBar from "../WSEditorToolBar";
import WSEditorCommandTree, { CommandTreeLeaf, CommandTreeNode } from "../WSEditorCommandTree";
import WSEditorCommandGroupContent, { DecodeResponseCommandGroup } from "../WSEditorCommandGroupContent";
import WSEditorCommandContent, { DecodeResponseCommand } from "../WSEditorCommandContent";
import WSEditorClientConfigDialog from "../WSEditorClientConfig";
import type {
  CommandGroup,
  ResponseCommandGroup,
  ResponseCommandGroups,
  Command,
  ResponseCommand,
} from "../interfaces";
import { workspaceApi, specsApi } from "../../../services";
import WSEditorExportDialog from "./WSEditorExportDialog";
import WSEditorDeleteDialog from "./WSEditorDeleteDialog";
import WSEditorSwaggerReloadDialog from "./WSEditorSwaggerReloadDialog";
import WSRenameDialog from "./WSRenameDialog";

interface CommandGroupMap {
  [id: string]: CommandGroup;
}

interface CommandMap {
  [id: string]: Command;
}

interface WSEditorProps {
  params: {
    workspaceName: string;
  };
}

interface WSEditorState {
  name: string;
  workspaceUrl: string;
  plane: string;
  source: string;
  clientConfigurable: boolean;

  selected: Command | CommandGroup | null;
  reloadTimestamp: number | null;
  expanded: Set<string>;

  commandMap: CommandMap;
  commandGroupMap: CommandGroupMap;
  commandTree: CommandTreeNode[];

  showSwaggerResourcePicker: boolean;
  showSwaggerReloadDialog: boolean;
  showClientConfigDialog: boolean;
  showExportDialog: boolean;
  showDeleteDialog: boolean;
  showModifyDialog: boolean;
}

const swaggerResourcePickerTransition = React.forwardRef(function swaggerResourcePickerTransition(
  props: TransitionProps & { children: React.ReactElement },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const drawerWidth = 300;

class WSEditor extends React.Component<WSEditorProps, WSEditorState> {
  constructor(props: WSEditorProps) {
    super(props);
    this.state = {
      name: this.props.params.workspaceName,
      workspaceUrl: `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}`,
      plane: "",
      source: "",
      clientConfigurable: false,
      selected: null,
      reloadTimestamp: null,
      expanded: new Set<string>(),
      commandMap: {},
      commandGroupMap: {},
      commandTree: [],
      showSwaggerResourcePicker: false,
      showSwaggerReloadDialog: false,
      showClientConfigDialog: false,
      showExportDialog: false,
      showDeleteDialog: false,
      showModifyDialog: false,
    };
  }

  componentDidMount() {
    this.loadWorkspace();
  }

  loadWorkspace = async (preSelectedId?: string | null) => {
    const { workspaceUrl } = this.state;
    if (preSelectedId === undefined) {
      preSelectedId = this.state.selected?.id;
    }

    try {
      const planeNames = await specsApi.getPlaneNames();
      const workspaceData = await workspaceApi.getWorkspace(workspaceUrl);
      const reloadTimestamp = Date.now();
      const commandMap: CommandMap = {};
      const commandGroupMap: CommandGroupMap = {};

      const buildCommand = (command_1: ResponseCommand): CommandTreeLeaf => {
        const cmd: Command = DecodeResponseCommand(command_1);
        commandMap[cmd.id] = cmd;
        return {
          id: cmd.id,
          names: [...cmd.names],
        };
      };

      const buildCommandGroup = (commandGroup_1: ResponseCommandGroup): CommandTreeNode => {
        const group: CommandGroup = DecodeResponseCommandGroup(commandGroup_1);

        commandGroupMap[group.id] = group;

        const node: CommandTreeNode = {
          id: group.id,
          names: [...group.names],
          canDelete: group.canDelete,
        };

        if (typeof commandGroup_1.commands === "object" && commandGroup_1.commands !== null) {
          node["leaves"] = [];

          for (const name in commandGroup_1.commands) {
            const subLeave = buildCommand(commandGroup_1.commands[name]);
            node["leaves"].push(subLeave);
          }
          node["leaves"].sort((a, b) => a.id.localeCompare(b.id));
          if (node["leaves"].length > 0) {
            node.canDelete = false;
          }
        }

        if (typeof commandGroup_1.commandGroups === "object" && commandGroup_1.commandGroups !== null) {
          node["nodes"] = [];
          for (const name_1 in commandGroup_1.commandGroups) {
            const subNode = buildCommandGroup(commandGroup_1.commandGroups[name_1]);
            node["nodes"].push(subNode);
            if (!subNode.canDelete) {
              node.canDelete = false;
            }
          }
          node["nodes"].sort((a_1, b_1) => a_1.id.localeCompare(b_1.id));
        }

        if ((node["leaves"]?.length ?? 0) > 1) {
          node.canDelete = false;
        }
        group.canDelete = node.canDelete;
        return node;
      };

      const commandTree: CommandTreeNode[] = [];

      if (workspaceData.commandTree.commandGroups) {
        const cmdGroups: ResponseCommandGroups = workspaceData.commandTree.commandGroups;
        for (const key in cmdGroups) {
          commandTree.push(buildCommandGroup(cmdGroups[key]));
        }
        commandTree.sort((a_2, b_2) => a_2.id.localeCompare(b_2.id));
      }

      let selected: Command | CommandGroup | null = null;

      if (preSelectedId != null) {
        if (preSelectedId.startsWith("command:")) {
          let id: string = preSelectedId;
          if (id in commandMap) {
            selected = commandMap[id];
          } else {
            id = "group:" + id.slice(8);
            let parts = id.split("/");
            while (parts.length > 1 && !(id in commandGroupMap)) {
              parts = parts.slice(0, -1);
              id = parts.join("/");
            }
            if (id in commandGroupMap) {
              selected = commandGroupMap[id];
            }
          }
        } else if (preSelectedId.startsWith("group:")) {
          let id_1: string = preSelectedId;
          let parts_1 = id_1.split("/");
          while (parts_1.length > 1 && !(id_1 in commandGroupMap)) {
            parts_1 = parts_1.slice(0, -1);
            id_1 = parts_1.join("/");
          }
          if (id_1 in commandGroupMap) {
            selected = commandGroupMap[id_1];
          }
        }
      }

      if (selected === null && commandTree.length > 0) {
        selected = commandGroupMap[commandTree[0].id];
      }

      const clientConfigurable = !planeNames.includes(workspaceData.plane);
      this.setState((preState) => {
        const newExpanded = new Set<string>();

        preState.expanded.forEach((value) => {
          if (value in commandGroupMap) {
            newExpanded.add(value);
          }
        });

        for (const groupId in commandGroupMap) {
          if (!(groupId in preState.commandGroupMap)) {
            newExpanded.add(groupId);
          }
        }

        return {
          ...preState,
          plane: workspaceData.plane,
          source: workspaceData.source,
          clientConfigurable: clientConfigurable,
          commandTree: commandTree,
          selected: selected,
          reloadTimestamp: reloadTimestamp,
          commandMap: commandMap,
          commandGroupMap: commandGroupMap,
          expanded: newExpanded,
        };
      });

      if (selected) {
        let expandedId = selected.id;
        if (expandedId.startsWith("command:")) {
          expandedId = expandedId.replace("command:", "group:").split("/").slice(0, -1).join("/");
        }
        const expandedIdParts = expandedId.split("/");
        this.setState((preState) => {
          const newExpanded = new Set(preState.expanded);
          expandedIdParts.forEach((_value, idx) => {
            newExpanded.add(expandedIdParts.slice(0, idx + 1).join("/"));
          });
          return {
            ...preState,
            expanded: newExpanded,
          };
        });
      }

      if (clientConfigurable) {
        const clientConfig = await this.getWorkspaceClientConfig(workspaceUrl);
        if (clientConfig == null) {
          this.showClientConfigDialog();
          return;
        }
      }

      if (commandTree.length === 0) {
        this.showSwaggerResourcePicker();
      }
    } catch (err) {
      return console.error(err);
    }
  };

  getWorkspaceClientConfig = async (workspaceUrl: string) => {
    return await workspaceApi.getWorkspaceClientConfig(workspaceUrl);
  };

  showClientConfigDialog = () => {
    this.setState({ showClientConfigDialog: true });
  };

  showSwaggerResourcePicker = () => {
    this.setState({ showSwaggerResourcePicker: true });
  };

  showSwaggerReloadDialog = () => {
    this.setState({ showSwaggerReloadDialog: true });
  };

  handleSwaggerReloadDialogClose = async (reloaded: boolean) => {
    if (reloaded) {
      await this.loadWorkspace();
    }
    this.setState({
      showSwaggerReloadDialog: false,
    });
  };

  handleSwaggerResourcePickerClose = (updated: boolean) => {
    if (updated) {
      this.loadWorkspace();
    }
    this.setState({
      showSwaggerResourcePicker: false,
    });
  };

  handleBackToHomepage = (blank: boolean) => {
    if (blank) {
      window.open("/?#/workspace", "_blank");
    } else {
      window.location.href = "/?#/workspace";
    }
  };

  handleGenerate = () => {
    this.setState({
      showExportDialog: true,
    });
  };

  handleGenerationClose = (_exported: boolean, showClientConfigDialog: boolean) => {
    this.setState({
      showExportDialog: false,
    });
    if (showClientConfigDialog) {
      this.setState({
        showClientConfigDialog: true,
      });
    }
  };

  handleDelete = () => {
    this.setState({
      showDeleteDialog: true,
    });
  };

  handleDeleteClose = (deleted: boolean) => {
    this.setState({
      showDeleteDialog: false,
    });
    if (deleted) {
      this.handleBackToHomepage(false);
    }
  };

  handleModify = () => {
    this.setState({
      showModifyDialog: true,
    });
  };

  handleModifyClose = (newWSName: string | null) => {
    this.setState({
      showModifyDialog: false,
    });
    if (!newWSName) {
      return;
    }
    setTimeout(() => {
      const target_url = `/?#/workspace/` + newWSName;
      window.location.href = target_url;
      window.location.reload();
    });
  };

  handleCommandTreeSelect = (nodeId: string) => {
    if (nodeId.startsWith("command:")) {
      this.setState((preState) => {
        const selected = preState.commandMap[nodeId];
        return {
          ...preState,
          selected: selected,
        };
      });
    } else if (nodeId.startsWith("group:")) {
      this.setState((preState) => {
        const selected = preState.commandGroupMap[nodeId];
        return {
          ...preState,
          selected: selected,
        };
      });
    }
  };

  handleCommandGroupUpdate = (commandGroup: CommandGroup | null) => {
    this.loadWorkspace(commandGroup?.id);
  };

  handleCommandUpdate = (command: Command | null) => {
    this.loadWorkspace(command?.id);
  };

  handleCommandTreeToggle = (nodeIds: string[]) => {
    const newExpanded = new Set(nodeIds);
    this.setState({
      expanded: newExpanded,
    });
  };

  handleClientConfigDialogClose = (updated: boolean) => {
    this.setState({
      showClientConfigDialog: false,
    });
    if (updated) {
      this.loadWorkspace();
    }
  };

  render() {
    const {
      showSwaggerResourcePicker,
      showSwaggerReloadDialog,
      showExportDialog,
      showDeleteDialog,
      showModifyDialog,
      plane,
      source,
      name,
      commandTree,
      selected,
      reloadTimestamp,
      workspaceUrl,
      expanded,
      showClientConfigDialog,
      clientConfigurable,
    } = this.state;
    const expandedIds: string[] = [];
    expanded.forEach((expandId) => {
      expandedIds.push(expandId);
    });
    return (
      <React.Fragment>
        <WSEditorToolBar
          workspaceName={name}
          onHomePage={() => {
            this.handleBackToHomepage(true);
          }}
          onGenerate={this.handleGenerate}
          onDelete={this.handleDelete}
          onModify={this.handleModify}
        ></WSEditorToolBar>

        <Box sx={{ display: "flex" }}>
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: "border-box" },
            }}
          >
            <Toolbar />
            {selected != null && (
              <WSEditorCommandTree
                commandTreeNodes={commandTree}
                onSelected={this.handleCommandTreeSelect}
                onToggle={this.handleCommandTreeToggle}
                onAdd={this.showSwaggerResourcePicker}
                onReload={this.showSwaggerReloadDialog}
                selected={selected!.id}
                expanded={expandedIds}
                onEditClientConfig={clientConfigurable ? this.showClientConfigDialog : undefined}
              />
            )}
          </Drawer>

          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 1,
            }}
          >
            <Toolbar sx={{ flexShrink: 0 }} />
            {selected != null && selected.id.startsWith("group:") && (
              <WSEditorCommandGroupContent
                workspaceUrl={workspaceUrl}
                commandGroup={selected as CommandGroup}
                reloadTimestamp={reloadTimestamp!}
                onUpdateCommandGroup={this.handleCommandGroupUpdate}
              />
            )}
            {selected != null && selected.id.startsWith("command:") && (
              <WSEditorCommandContent
                workspaceUrl={workspaceUrl}
                previewCommand={selected as Command}
                reloadTimestamp={reloadTimestamp!}
                onUpdateCommand={this.handleCommandUpdate}
              />
            )}
          </Box>
        </Box>

        <Dialog
          fullScreen
          open={showSwaggerResourcePicker}
          onClose={this.handleSwaggerResourcePickerClose}
          TransitionComponent={swaggerResourcePickerTransition}
        >
          <WSEditorSwaggerPicker plane={plane} workspaceName={name} onClose={this.handleSwaggerResourcePickerClose} />
        </Dialog>
        {showModifyDialog && (
          <WSRenameDialog
            workspaceUrl={workspaceUrl}
            workspaceName={name}
            open={showModifyDialog}
            onClose={this.handleModifyClose}
          />
        )}
        {showDeleteDialog && (
          <WSEditorDeleteDialog workspaceName={name} open={showDeleteDialog} onClose={this.handleDeleteClose} />
        )}
        {showExportDialog && (
          <WSEditorExportDialog
            workspaceUrl={workspaceUrl}
            open={showExportDialog}
            clientConfigurable={clientConfigurable}
            onClose={this.handleGenerationClose}
          />
        )}
        {showSwaggerReloadDialog && (
          <WSEditorSwaggerReloadDialog
            workspaceUrl={workspaceUrl}
            workspaceName={name}
            source={source}
            open={showSwaggerReloadDialog}
            onClose={this.handleSwaggerReloadDialogClose}
          />
        )}
        {showClientConfigDialog && (
          <WSEditorClientConfigDialog
            workspaceUrl={workspaceUrl}
            open={showClientConfigDialog}
            onClose={this.handleClientConfigDialogClose}
          />
        )}
      </React.Fragment>
    );
  }
}

const WSEditorWrapper = (props: any) => {
  const params = useParams();

  return <WSEditor params={params} {...props} />;
};

export { WSEditorWrapper as WSEditor };
export default WSEditor;
