import React, { useState, Fragment } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Alert } from "@mui/material";
import { workspaceApi, errorHandlerApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import { AsyncOperationBanner } from "../../../../components";

interface WSEditorDeleteDialogProps {
  workspaceName: string;
  open: boolean;
  onClose: (deleted: boolean) => void;
}

const WSEditorDeleteDialog: React.FC<WSEditorDeleteDialogProps> = ({ workspaceName, open, onClose }) => {
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [confirmName, setConfirmName] = useState<string | undefined>(undefined);

  const deleteWorkspaceOperation = useAsyncOperation(workspaceApi.deleteWorkspace);

  const handleClose = () => {
    onClose(false);
  };

  const handleDelete = async () => {
    try {
      await deleteWorkspaceOperation.execute(workspaceName);
      onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
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
        <AsyncOperationBanner operation={deleteWorkspaceOperation} />
        {!deleteWorkspaceOperation.loading && (
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
