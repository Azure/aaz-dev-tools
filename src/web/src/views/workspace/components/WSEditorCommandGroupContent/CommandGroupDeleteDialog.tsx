import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Typography } from "@mui/material";
import { commandApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import { AsyncOperationBanner } from "../../../../components";
import * as React from "react";
import { COMMAND_PREFIX } from "../../../../constants";
import type { CommandGroup } from "../../interfaces";

interface CommandGroupDeleteDialogProps {
  workspaceUrl: string;
  open: boolean;
  commandGroup: CommandGroup;
  onClose: (deleted: boolean) => void;
}

const CommandGroupDeleteDialog: React.FC<CommandGroupDeleteDialogProps> = ({
  workspaceUrl,
  open,
  commandGroup,
  onClose,
}) => {
  const deleteCommandGroupOperation = useAsyncOperation(commandApi.deleteCommandGroup);

  const handleClose = React.useCallback(() => {
    onClose(false);
  }, [onClose]);

  const handleDelete = React.useCallback(async () => {
    const nodeUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/${commandGroup.names.join("/")}`;

    try {
      await deleteCommandGroupOperation.execute(nodeUrl);
      onClose(true);
    } catch (err: any) {
      console.error(err);
    }
  }, [workspaceUrl, commandGroup.names, onClose, deleteCommandGroupOperation]);

  return (
    <Dialog disableEscapeKeyDown open={open}>
      <DialogTitle>Delete Command Group</DialogTitle>
      <DialogContent dividers={true}>
        <AsyncOperationBanner operation={deleteCommandGroupOperation} />
        <Typography variant="body2">{`${COMMAND_PREFIX}${commandGroup.names.join(" ")}`}</Typography>
      </DialogContent>
      <DialogActions>
        {!deleteCommandGroupOperation.loading && (
          <React.Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleDelete}>Delete</Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CommandGroupDeleteDialog;
