import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  InputLabel,
  LinearProgress,
  Radio,
  RadioGroup,
  TextField,
} from "@mui/material";
import { commandApi, errorHandlerApi } from "../../services";
import * as React from "react";
import { CommandGroup, DecodeResponseCommandGroup } from "./WSEditorCommandGroupContent";

interface CommandGroupDialogProps {
  workspaceUrl: string;
  open: boolean;
  commandGroup: CommandGroup;
  onClose: (newCommandGroup?: CommandGroup) => void;
}

interface CommandGroupDialogState {
  name: string;
  stage: string;
  shortHelp: string;
  longHelp: string;
  invalidText?: string;
  updating: boolean;
}

class CommandGroupDialog extends React.Component<CommandGroupDialogProps, CommandGroupDialogState> {
  constructor(props: CommandGroupDialogProps) {
    super(props);
    this.state = {
      name: this.props.commandGroup.names.join(" "),
      shortHelp: this.props.commandGroup.help?.short ?? "",
      longHelp: this.props.commandGroup.help?.lines?.join("\n") ?? "",
      stage: this.props.commandGroup.stage,
      updating: false,
    };
  }

  handleModify = async () => {
    let { name, shortHelp, longHelp } = this.state;
    const { stage } = this.state;
    const { workspaceUrl, commandGroup } = this.props;

    name = name.trim();
    shortHelp = shortHelp.trim();
    longHelp = longHelp.trim();

    const names = name.split(" ").filter((n) => n.length > 0);

    this.setState({
      invalidText: undefined,
    });

    if (names.length < 1) {
      this.setState({
        invalidText: `Field 'Name' is required.`,
      });
      return;
    }

    for (const idx in names) {
      const piece = names[idx];
      if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
        this.setState({
          invalidText: `Invalid Name part: '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `,
        });
        return;
      }
    }

    if (shortHelp.length < 1) {
      this.setState({
        invalidText: `Field 'Short Summary' is required.`,
      });
    }

    let lines: string[] = [];
    if (longHelp.length > 1) {
      lines = longHelp.split("\n").filter((l) => l.length > 0);
    }

    this.setState({
      updating: true,
    });

    const nodeUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/` + commandGroup.names.join("/");

    try {
      const res = await commandApi.updateCommandGroup(nodeUrl, {
        help: {
          short: shortHelp,
          lines: lines,
        },
        stage: stage,
      });

      const name = names.join(" ");
      if (name === commandGroup.names.join(" ")) {
        const cmdGroup = DecodeResponseCommandGroup(res);
        this.setState({
          updating: false,
        });
        this.props.onClose(cmdGroup);
      } else {
        const renameRes = await commandApi.renameCommandGroup(nodeUrl, name);
        const cmdGroup = DecodeResponseCommandGroup(renameRes);
        this.setState({
          updating: false,
        });
        this.props.onClose(cmdGroup);
      }
    } catch (err: any) {
      console.error(err);
      this.setState({
        updating: false,
        invalidText: errorHandlerApi.getErrorMessage(err),
      });
    }
  };

  handleClose = () => {
    this.setState({
      invalidText: undefined,
    });
    this.props.onClose();
  };

  render() {
    const { name, shortHelp, longHelp, invalidText, updating, stage } = this.state;
    return (
      <Dialog disableEscapeKeyDown open={this.props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
        <DialogTitle>Command Group</DialogTitle>
        <DialogContent dividers={true}>
          {invalidText && (
            <Alert variant="filled" severity="error">
              {" "}
              {invalidText}{" "}
            </Alert>
          )}

          <InputLabel required shrink sx={{ font: "inherit" }}>
            Stage
          </InputLabel>
          <RadioGroup
            row
            value={stage}
            name="stage"
            onChange={(event: any) => {
              this.setState({
                stage: event.target.value,
              });
            }}
          >
            <FormControlLabel value="Stable" control={<Radio />} label="Stable" sx={{ ml: 4 }} />
            <FormControlLabel value="Preview" control={<Radio />} label="Preview" sx={{ ml: 4 }} />
            <FormControlLabel value="Experimental" control={<Radio />} label="Experimental" sx={{ ml: 4 }} />
          </RadioGroup>

          <TextField
            id="name"
            label="Name"
            type="text"
            fullWidth
            variant="standard"
            value={name}
            onChange={(event: any) => {
              this.setState({
                name: event.target.value,
              });
            }}
            margin="normal"
            required
          />
          <TextField
            id="shortSummary"
            label="Short Summary"
            type="text"
            fullWidth
            variant="standard"
            value={shortHelp}
            onChange={(event: any) => {
              this.setState({
                shortHelp: event.target.value,
              });
            }}
            margin="normal"
            required
          />
          <TextField
            id="longSummary"
            label="Long Summary"
            helperText="Please add long summary in lines."
            type="text"
            fullWidth
            multiline
            rows={4}
            variant="standard"
            value={longHelp}
            onChange={(event: any) => {
              this.setState({
                longHelp: event.target.value,
              });
            }}
            margin="normal"
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

export default CommandGroupDialog;
