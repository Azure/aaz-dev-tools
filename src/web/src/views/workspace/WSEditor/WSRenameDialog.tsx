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

interface WSRenameDialogProps {
  workspaceUrl: string;
  workspaceName: string;
  open: boolean;
  onClose: (newWSName: string | null) => void;
}

interface WSRenameDialogState {
  newWSName: string;
  invalidText?: string;
  updating: boolean;
}

class WSRenameDialog extends React.Component<WSRenameDialogProps, WSRenameDialogState> {
  constructor(props: WSRenameDialogProps) {
    super(props);
    this.state = {
      newWSName: this.props.workspaceName,
      updating: false,
    };
  }

  handleModify = () => {
    const { newWSName } = this.state;
    const { workspaceUrl, workspaceName } = this.props;

    const nName = newWSName.trim();
    if (nName.length < 1) {
      this.setState({
        invalidText: `Field 'Name' is required.`,
      });
      return;
    }

    this.setState({
      invalidText: undefined,
    });
    this.setState({
      updating: true,
    });

    if (workspaceName === nName) {
      this.setState({
        updating: false,
      });
      this.props.onClose(null);
    } else {
      workspaceApi
        .renameWorkspace(workspaceUrl, nName)
        .then((res: any) => {
          this.setState({
            updating: false,
          });
          this.props.onClose(res.name);
        })
        .catch((err: any) => {
          this.setState({
            updating: false,
            invalidText: errorHandlerApi.getErrorMessage(err),
          });
        });
    }
  };

  handleClose = () => {
    this.setState({
      invalidText: undefined,
    });
    this.props.onClose(null);
  };

  render() {
    const { invalidText, updating } = this.state;
    return (
      <Dialog disableEscapeKeyDown open={this.props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
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
            value={this.state.newWSName}
            onChange={(event: any) => {
              this.setState({
                newWSName: event.target.value,
              });
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
              <Button onClick={this.handleClose}>Cancel</Button>
              <Button onClick={this.handleModify}>Save</Button>
            </React.Fragment>
          )}
        </DialogActions>
      </Dialog>
    );
  }
}

export default WSRenameDialog;
