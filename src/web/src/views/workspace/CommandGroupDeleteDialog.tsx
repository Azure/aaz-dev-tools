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
import { CommandGroup } from "./WSEditorCommandGroupContent";

const commandPrefix = "az ";

function CommandGroupDeleteDialog(props: {
  workspaceUrl: string;
  open: boolean;
  commandGroup: CommandGroup;
  onClose: (deleted: boolean) => void;
}) {
  const [updating, setUpdating] = React.useState<boolean>(false);

  const handleClose = () => {
    props.onClose(false);
  };
  const handleDelete = async () => {
    const nodeUrl = `${props.workspaceUrl}/CommandTree/Nodes/aaz/` + props.commandGroup.names.join("/");
    setUpdating(true);

    try {
      await commandApi.deleteCommandGroup(nodeUrl);
      setUpdating(false);
      props.onClose(true);
    } catch (err: any) {
      setUpdating(false);
      console.error(err);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>Delete Command Group</DialogTitle>
      <DialogContent dividers={true}>
        <Typography variant="body2">{`${commandPrefix}${props.commandGroup.names.join(" ")}`}</Typography>
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
}

export default CommandGroupDeleteDialog;
