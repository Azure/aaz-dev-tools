import React, { useState, Fragment } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Alert } from "@mui/material";
import { workspaceApi, errorHandlerApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import { AsyncOperationBanner } from "../../../../components";

interface WSRenameDialogProps {
  workspaceUrl: string;
  workspaceName: string;
  open: boolean;
  onClose: (newWSName: string | null) => void;
}

const WSRenameDialog: React.FC<WSRenameDialogProps> = ({ workspaceUrl, workspaceName, open, onClose }) => {
  const [newWSName, setNewWSName] = useState<string>(workspaceName);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);

  const renameWorkspaceOperation = useAsyncOperation(workspaceApi.renameWorkspace);

  const handleModify = async () => {
    const nName = newWSName.trim();
    if (nName.length < 1) {
      setInvalidText(`Field 'Name' is required.`);
      return;
    }

    setInvalidText(undefined);

    if (workspaceName === nName) {
      onClose(null);
    } else {
      try {
        const res = await renameWorkspaceOperation.execute(workspaceUrl, nName);
        onClose(res?.name || nName);
      } catch (err: any) {
        setInvalidText(errorHandlerApi.getErrorMessage(err));
      }
    }
  };

  const handleClose = () => {
    setInvalidText(undefined);
    onClose(null);
  };

  return (
    <Dialog disableEscapeKeyDown open={open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      <DialogTitle>Rename Workspace</DialogTitle>
      <DialogContent dividers={true}>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        <TextField
          id="name"
          label="Name"
          type="text"
          fullWidth
          variant="standard"
          value={newWSName}
          onChange={(event: any) => {
            setNewWSName(event.target.value);
          }}
          margin="normal"
          required
        />
      </DialogContent>
      <DialogActions>
        <AsyncOperationBanner operation={renameWorkspaceOperation} />
        {!renameWorkspaceOperation.loading && (
          <Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleModify}>Save</Button>
          </Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default WSRenameDialog;
