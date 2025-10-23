import React, { useState, Fragment } from "react";
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
import { workspaceApi, errorHandlerApi } from "../../../../services";

interface WSEditorDeleteDialogProps {
  workspaceName: string;
  open: boolean;
  onClose: (deleted: boolean) => void;
}

const WSEditorDeleteDialog: React.FC<WSEditorDeleteDialogProps> = ({ workspaceName, open, onClose }) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [confirmName, setConfirmName] = useState<string | undefined>(undefined);

  const handleClose = () => {
    onClose(false);
  };

  const handleDelete = async () => {
    setUpdating(true);
    try {
      await workspaceApi.deleteWorkspace(workspaceName);
      setUpdating(false);
      onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={open}>
      <DialogTitle>Delete '{workspaceName}' workspace?</DialogTitle>
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
          <Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleDelete} disabled={workspaceName !== confirmName}>
              Confirm
            </Button>
          </Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default WSEditorDeleteDialog;
