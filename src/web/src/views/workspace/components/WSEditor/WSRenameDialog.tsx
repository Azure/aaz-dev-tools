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

interface WSRenameDialogProps {
  workspaceUrl: string;
  workspaceName: string;
  open: boolean;
  onClose: (newWSName: string | null) => void;
}

const WSRenameDialog: React.FC<WSRenameDialogProps> = ({ workspaceUrl, workspaceName, open, onClose }) => {
  const [newWSName, setNewWSName] = useState<string>(workspaceName);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [updating, setUpdating] = useState<boolean>(false);

  const handleModify = () => {
    const nName = newWSName.trim();
    if (nName.length < 1) {
      setInvalidText(`Field 'Name' is required.`);
      return;
    }

    setInvalidText(undefined);
    setUpdating(true);

    if (workspaceName === nName) {
      setUpdating(false);
      onClose(null);
    } else {
      workspaceApi
        .renameWorkspace(workspaceUrl, nName)
        .then((res: any) => {
          setUpdating(false);
          onClose(res.name);
        })
        .catch((err: any) => {
          setUpdating(false);
          setInvalidText(errorHandlerApi.getErrorMessage(err));
        });
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
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
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
