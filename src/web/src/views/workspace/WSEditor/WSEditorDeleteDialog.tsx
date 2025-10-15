import * as React from "react";
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Button,
  TextField,
  Alert,
} from "@mui/material";
import { workspaceApi, errorHandlerApi } from "../../../services";

interface WSEditorDeleteDialogProps {
  workspaceName: string;
  open: boolean;
  onClose: (deleted: boolean) => void;
}

function WSEditorDeleteDialog(props: WSEditorDeleteDialogProps) {
  const [updating, setUpdating] = React.useState<boolean>(false);
  const [invalidText, setInvalidText] = React.useState<string | undefined>(undefined);
  const [confirmName, setConfirmName] = React.useState<string | undefined>(undefined);

  const handleClose = () => {
    props.onClose(false);
  };

  const handleDelete = () => {
    setUpdating(true);
    workspaceApi
      .deleteWorkspace(props.workspaceName)
      .then(() => {
        setUpdating(false);
        props.onClose(true);
      })
      .catch((err: any) => {
        console.error(err);
        setInvalidText(errorHandlerApi.getErrorMessage(err));
        setUpdating(false);
      });
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>Delete '{props.workspaceName}' workspace?</DialogTitle>
      <DialogContent dividers={true}>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        <TextField
          id="name"
          label="Workspace Name"
          helperText="Please type workspace name to confirm."
          type="text"
          fullWidth
          variant="standard"
          value={confirmName}
          onChange={(event: any) => {
            setConfirmName(event.target.value);
          }}
          margin="normal"
          required
        />
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
            <Button onClick={handleDelete} disabled={props.workspaceName !== confirmName}>
              Confirm
            </Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default WSEditorDeleteDialog;
