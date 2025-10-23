import React, { useEffect, useCallback } from "react";
import { Box, Dialog, Slide, Drawer, Toolbar } from "@mui/material";
import { useParams } from "react-router";
import { TransitionProps } from "@mui/material/transitions";
import WSEditorSwaggerPicker from "../../components/WSEditorSwaggerPicker";
import WSEditorToolBar from "./WSEditorToolBar";
import WSEditorCommandTree from "./WSEditorCommandTree";
import WSEditorCommandGroupContent from "../WSEditorCommandGroupContent";
import WSEditorCommandContent from "../WSEditorCommandContent";
import WSEditorClientConfigDialog from "./WSEditorClientConfig";
import type { CommandGroup, Command } from "../../interfaces";
import WSEditorExportDialog from "./WSEditorExportDialog";
import WSEditorDeleteDialog from "./WSEditorDeleteDialog";
import WSEditorSwaggerReloadDialog from "./WSEditorSwaggerReloadDialog";
import WSRenameDialog from "./WSRenameDialog";
import { useDialogManager, useWorkspaceData, useTreeState } from "../../hooks/index";

interface WSEditorProps {
  params: {
    workspaceName: string;
  };
}

const swaggerResourcePickerTransition = React.forwardRef(function swaggerResourcePickerTransition(
  props: TransitionProps & { children: React.ReactElement },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const drawerWidth = 300;

const WSEditor = ({ params }: WSEditorProps) => {
  const { workspaceName } = params;

  const dialogManager = useDialogManager();
  const workspace = useWorkspaceData(workspaceName);
  const treeState = useTreeState(workspace.commandMap, workspace.commandGroupMap, workspace.commandTree);

  useEffect(() => {
    workspace.loadWorkspace();
  }, [workspace.loadWorkspace]);

  useEffect(() => {
    if (!workspace.reloadTimestamp) return;

    const checkClientConfig = async () => {
      if (workspace.clientConfigurable) {
        try {
          const clientConfig = await workspace.getWorkspaceClientConfig(workspace.workspaceUrl);
          if (!clientConfig) {
            dialogManager.openClientConfigDialog();
          }
        } catch (error) {
          console.error(error);
        }
      }
    };

    checkClientConfig();

    if (workspace.commandTree.length === 0) {
      dialogManager.openSwaggerResourcePicker();
    }
  }, [workspace.reloadTimestamp]);

  useEffect(() => {
    if (Object.keys(workspace.commandGroupMap).length > 0) {
      treeState.updateExpanded(workspace.commandGroupMap, undefined, true);
    }
  }, [workspace.commandGroupMap, treeState.updateExpanded]);

  const handleSwaggerReloadDialogClose = useCallback(
    async (reloaded: boolean) => {
      if (reloaded) {
        await workspace.loadWorkspace();
      }
      dialogManager.closeSwaggerReloadDialog();
    },
    [workspace.loadWorkspace, dialogManager.closeSwaggerReloadDialog],
  );

  const handleSwaggerResourcePickerClose = useCallback(
    (updated: boolean) => {
      if (updated) {
        workspace.loadWorkspace();
      }
      dialogManager.closeSwaggerResourcePicker();
    },
    [workspace.loadWorkspace, dialogManager.closeSwaggerResourcePicker],
  );

  const handleBackToHomepage = useCallback((blank: boolean) => {
    if (blank) {
      window.open("/?#/workspace", "_blank");
    } else {
      window.location.href = "/?#/workspace";
    }
  }, []);

  const handleGenerate = useCallback(() => {
    dialogManager.openExportDialog();
  }, [dialogManager]);

  const handleGenerationClose = useCallback(
    (_exported: boolean, showClientConfigDialog: boolean) => {
      dialogManager.closeExportDialog();
      if (showClientConfigDialog) {
        dialogManager.openClientConfigDialog();
      }
    },
    [dialogManager],
  );

  const handleDelete = useCallback(() => {
    dialogManager.openDeleteDialog();
  }, [dialogManager]);

  const handleDeleteClose = useCallback(
    (deleted: boolean) => {
      dialogManager.closeDeleteDialog();
      if (deleted) {
        handleBackToHomepage(false);
      }
    },
    [dialogManager, handleBackToHomepage],
  );

  const handleModify = useCallback(() => {
    dialogManager.openModifyDialog();
  }, [dialogManager]);

  const handleModifyClose = useCallback(
    (newWSName: string | null) => {
      dialogManager.closeModifyDialog();
      if (!newWSName) {
        return;
      }
      setTimeout(() => {
        const target_url = `/?#/workspace/` + newWSName;
        window.location.href = target_url;
        window.location.reload();
      });
    },
    [dialogManager],
  );

  const handleCommandGroupUpdate = useCallback(
    async (commandGroup: CommandGroup | null) => {
      if (commandGroup) {
        await workspace.loadWorkspace();
        treeState.setSelected(commandGroup);
      } else {
        treeState.setSelected(null);
        await workspace.loadWorkspace();
      }
    },
    [workspace.loadWorkspace, treeState.setSelected],
  );

  const handleCommandUpdate = useCallback(
    async (command: Command | null) => {
      if (command) {
        await workspace.loadWorkspace();
        treeState.setSelected(command);
      } else {
        treeState.setSelected(null);
        await workspace.loadWorkspace();
      }
    },
    [workspace.loadWorkspace, treeState.setSelected],
  );

  const handleClientConfigDialogClose = useCallback(
    (updated: boolean) => {
      dialogManager.closeClientConfigDialog();
      if (updated) {
        workspace.loadWorkspace();
      }
    },
    [dialogManager.closeClientConfigDialog, workspace.loadWorkspace],
  );

  const expandedIds: string[] = Array.from(treeState.expanded);

  return (
    <>
      <WSEditorToolBar
        workspaceName={workspace.name}
        onHomePage={() => {
          handleBackToHomepage(true);
        }}
        onGenerate={handleGenerate}
        onDelete={handleDelete}
        onModify={handleModify}
      />

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
          {treeState.selected != null && (
            <WSEditorCommandTree
              commandTreeNodes={workspace.commandTree}
              onSelected={treeState.handleCommandTreeSelect}
              onToggle={treeState.handleCommandTreeToggle}
              onAdd={dialogManager.openSwaggerResourcePicker}
              onReload={dialogManager.openSwaggerReloadDialog}
              selected={treeState.selected.id}
              expanded={expandedIds}
              onEditClientConfig={workspace.clientConfigurable ? dialogManager.openClientConfigDialog : undefined}
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
          {treeState.selected != null && treeState.selected.id.startsWith("group:") && (
            <WSEditorCommandGroupContent
              key={treeState.selected.id}
              workspaceUrl={workspace.workspaceUrl}
              commandGroup={treeState.selected as CommandGroup}
              reloadTimestamp={workspace.reloadTimestamp!}
              onUpdateCommandGroup={handleCommandGroupUpdate}
            />
          )}
          {treeState.selected != null && treeState.selected.id.startsWith("command:") && (
            <WSEditorCommandContent
              key={treeState.selected.id}
              workspaceUrl={workspace.workspaceUrl}
              previewCommand={treeState.selected as Command}
              reloadTimestamp={workspace.reloadTimestamp!}
              onUpdateCommand={handleCommandUpdate}
            />
          )}
        </Box>
      </Box>

      <Dialog
        fullScreen
        open={dialogManager.showSwaggerResourcePicker}
        onClose={handleSwaggerResourcePickerClose}
        TransitionComponent={swaggerResourcePickerTransition}
      >
        <WSEditorSwaggerPicker
          plane={workspace.plane}
          workspaceName={workspace.name}
          onClose={handleSwaggerResourcePickerClose}
        />
      </Dialog>
      {dialogManager.showModifyDialog && (
        <WSRenameDialog
          workspaceUrl={workspace.workspaceUrl}
          workspaceName={workspace.name}
          open={dialogManager.showModifyDialog}
          onClose={handleModifyClose}
        />
      )}
      {dialogManager.showDeleteDialog && (
        <WSEditorDeleteDialog
          workspaceName={workspace.name}
          open={dialogManager.showDeleteDialog}
          onClose={handleDeleteClose}
        />
      )}
      {dialogManager.showExportDialog && (
        <WSEditorExportDialog
          workspaceUrl={workspace.workspaceUrl}
          open={dialogManager.showExportDialog}
          clientConfigurable={workspace.clientConfigurable}
          onClose={handleGenerationClose}
        />
      )}
      {dialogManager.showSwaggerReloadDialog && (
        <WSEditorSwaggerReloadDialog
          workspaceUrl={workspace.workspaceUrl}
          workspaceName={workspace.name}
          source={workspace.source}
          open={dialogManager.showSwaggerReloadDialog}
          onClose={handleSwaggerReloadDialogClose}
        />
      )}
      {dialogManager.showClientConfigDialog && (
        <WSEditorClientConfigDialog
          workspaceUrl={workspace.workspaceUrl}
          open={dialogManager.showClientConfigDialog}
          onClose={handleClientConfigDialogClose}
        />
      )}
    </>
  );
};

const WSEditorWrapper = (props: any) => {
  const params = useParams();

  return <WSEditor params={params} {...props} />;
};

export { WSEditorWrapper as WSEditor };
export default WSEditor;
