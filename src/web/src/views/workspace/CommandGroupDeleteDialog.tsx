import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  Typography,
} from "@mui/material";
import { commandApi } from "../../services";
import * as React from "react";
import { COMMAND_PREFIX } from "../../constants";
import type { CommandGroup } from "./interfaces";

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
  const [updating, setUpdating] = React.useState<boolean>(false);

  const handleClose = React.useCallback(() => {
    onClose(false);
  }, [onClose]);

  const handleDelete = React.useCallback(async () => {
    const nodeUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/${commandGroup.names.join("/")}`;
    setUpdating(true);

    try {
      await commandApi.deleteCommandGroup(nodeUrl);
      setUpdating(false);
      onClose(true);
    } catch (err: any) {
      setUpdating(false);
      console.error(err);
    }
  }, [workspaceUrl, commandGroup.names, onClose]);

  return (
    <Dialog disableEscapeKeyDown open={open}>
      <DialogTitle>Delete Command Group</DialogTitle>
      <DialogContent dividers={true}>
        <Typography variant="body2">{`${COMMAND_PREFIX}${commandGroup.names.join(" ")}`}</Typography>
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
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
