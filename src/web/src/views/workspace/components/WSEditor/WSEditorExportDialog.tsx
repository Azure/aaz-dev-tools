import React, { useState, useEffect, Fragment } from "react";
import { Box, Dialog, DialogTitle, DialogContent, DialogActions, LinearProgress, Button, Alert } from "@mui/material";
import { workspaceApi, errorHandlerApi } from "../../../../services";

interface WSEditorExportDialogProps {
  workspaceUrl: string;
  open: boolean;
  clientConfigurable: boolean;
  onClose: (exported: boolean, showClientConfigDialog: boolean) => void;
}

const WSEditorExportDialog: React.FC<WSEditorExportDialogProps> = ({
  workspaceUrl,
  open,
  clientConfigurable,
  onClose,
}) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [clientConfigOOD, setClientConfigOOD] = useState<boolean>(false);

  useEffect(() => {
    if (clientConfigurable) {
      verifyClientConfig();
    }
  }, [clientConfigurable]);

  const handleClose = () => {
    onClose(false, false);
  };

  const verifyClientConfig = async () => {
    setUpdating(true);
    try {
      await workspaceApi.verifyClientConfig(workspaceUrl);
      setClientConfigOOD(false);
      setUpdating(false);
    } catch (err: any) {
      // catch 409 error
      if (errorHandlerApi.isHttpError(err, 409)) {
        setInvalidText(`The client config in this workspace is out of date. Please refresh it first.`);
        setClientConfigOOD(true);
        setUpdating(false);
        return;
      } else {
        console.error(err);
        setInvalidText(errorHandlerApi.getErrorMessage(err));
        setUpdating(false);
      }
    }
  };

  const inheritClientConfig = async () => {
    setUpdating(true);
    try {
      await workspaceApi.inheritClientConfig(workspaceUrl);
      setClientConfigOOD(false);
      setUpdating(false);
      onClose(false, true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const handleExport = async () => {
    setUpdating(true);

    try {
      await workspaceApi.generateWorkspace(workspaceUrl);
      setUpdating(false);
      onClose(false, false);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={open}>
      <DialogTitle>Export workspace command models to AAZ Repo</DialogTitle>
      <DialogContent>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
          <Fragment>
            {clientConfigOOD && <Button onClick={inheritClientConfig}>Refresh Client Config</Button>}
            {!clientConfigOOD && <Button onClick={handleClose}>Cancel</Button>}
            {!clientConfigOOD && <Button onClick={handleExport}>Confirm</Button>}
          </Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default WSEditorExportDialog;
