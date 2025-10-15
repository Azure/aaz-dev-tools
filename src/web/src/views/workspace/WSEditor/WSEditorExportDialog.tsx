import * as React from "react";
import { Box, Dialog, DialogTitle, DialogContent, DialogActions, LinearProgress, Button, Alert } from "@mui/material";
import { workspaceApi, errorHandlerApi } from "../../../services";

interface WSEditorExportDialogProps {
  workspaceUrl: string;
  open: boolean;
  clientConfigurable: boolean;
  onClose: (exported: boolean, showClientConfigDialog: boolean) => void;
}

interface WSEditorExportDialogState {
  updating: boolean;
  invalidText: string | undefined;
  clientConfigOOD: boolean;
}

class WSEditorExportDialog extends React.Component<WSEditorExportDialogProps, WSEditorExportDialogState> {
  constructor(props: WSEditorExportDialogProps) {
    super(props);
    this.state = {
      updating: false,
      invalidText: undefined,
      clientConfigOOD: false,
    };
  }

  componentDidMount(): void {
    if (this.props.clientConfigurable) {
      this.verifyClientConfig();
    }
  }

  handleClose = () => {
    this.props.onClose(false, false);
  };

  verifyClientConfig = async () => {
    this.setState({ updating: true });
    try {
      await workspaceApi.verifyClientConfig(this.props.workspaceUrl);
      this.setState({ clientConfigOOD: false, updating: false });
    } catch (err: any) {
      // catch 409 error
      if (errorHandlerApi.isHttpError(err, 409)) {
        this.setState({
          invalidText: `The client config in this workspace is out of date. Please refresh it first.`,
          clientConfigOOD: true,
          updating: false,
        });
        return;
      } else {
        console.error(err);
        this.setState({
          invalidText: errorHandlerApi.getErrorMessage(err),
          updating: false,
        });
      }
    }
  };

  inheritClientConfig = async () => {
    this.setState({ updating: true });
    try {
      await workspaceApi.inheritClientConfig(this.props.workspaceUrl);
      this.setState({ clientConfigOOD: false, updating: false });
      this.props.onClose(false, true);
    } catch (err: any) {
      console.error(err);
      this.setState({
        invalidText: errorHandlerApi.getErrorMessage(err),
        updating: false,
      });
    }
  };

  handleExport = async () => {
    this.setState({ updating: true });

    try {
      await workspaceApi.generateWorkspace(this.props.workspaceUrl);
      this.setState({ updating: false });
      this.props.onClose(false, false);
    } catch (err: any) {
      console.error(err);
      this.setState({
        invalidText: errorHandlerApi.getErrorMessage(err),
        updating: false,
      });
    }
  };

  render(): React.ReactNode {
    const { updating, invalidText, clientConfigOOD } = this.state;
    return (
      <Dialog disableEscapeKeyDown open={this.props.open}>
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
            <React.Fragment>
              {clientConfigOOD && <Button onClick={this.inheritClientConfig}>Refresh Client Config</Button>}
              {!clientConfigOOD && <Button onClick={this.handleClose}>Cancel</Button>}
              {!clientConfigOOD && <Button onClick={this.handleExport}>Confirm</Button>}
            </React.Fragment>
          )}
        </DialogActions>
      </Dialog>
    );
  }
}

export default WSEditorExportDialog;
