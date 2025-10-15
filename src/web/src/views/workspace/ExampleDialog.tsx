import {
  styled,
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Input,
  InputAdornment,
  InputLabel,
  LinearProgress,
  TextField,
  Typography,
  TypographyProps,
  Stack,
} from "@mui/material";
import React from "react";
import DoDisturbOnRoundedIcon from "@mui/icons-material/DoDisturbOnRounded";
import AddCircleRoundedIcon from "@mui/icons-material/AddCircleRounded";
import CloseIcon from "@mui/icons-material/Close";
import { commandApi, errorHandlerApi } from "../../services";
import { COMMAND_PREFIX } from "../../constants";
import { ExampleItemSelector } from "./WSEditorExamplePicker";
import { Command, Example, DecodeResponseCommand } from "./WSEditorCommandContent";

export interface ExampleDialogProps {
  workspaceUrl: string;
  open: boolean;
  command: Command;
  idx?: number;
  onClose: (newCommand?: Command) => void;
}

interface ExampleDialogState {
  name: string;
  exampleCommands: string[];
  isAdd: boolean;
  invalidText?: string;
  updating: boolean;
  source?: string;
  exampleOptions: Example[];
}

const ExampleCommandTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 400,
}));

class ExampleDialog extends React.Component<ExampleDialogProps, ExampleDialogState> {
  constructor(props: ExampleDialogProps) {
    super(props);
    const examples: Example[] = this.props.command.examples ?? [];
    if (this.props.idx === undefined) {
      this.state = {
        name: "",
        exampleCommands: [""],
        isAdd: true,
        invalidText: undefined,
        updating: false,
        source: undefined,
        exampleOptions: [],
      };
    } else {
      const example = examples[this.props.idx];
      this.state = {
        name: example.name,
        exampleCommands: example.commands,
        isAdd: false,
        invalidText: undefined,
        updating: false,
        source: undefined,
        exampleOptions: [],
      };
    }
  }

  onUpdateExamples = async (examples: Example[]) => {
    const { workspaceUrl, command } = this.props;

    const leafUrl =
      `${workspaceUrl}/CommandTree/Nodes/aaz/` +
      command.names.slice(0, -1).join("/") +
      "/Leaves/" +
      command.names[command.names.length - 1];

    this.setState({
      updating: true,
    });

    try {
      const responseData = await commandApi.updateCommandExamples(leafUrl, examples);
      const cmd = DecodeResponseCommand(responseData);
      this.setState({
        updating: false,
      });
      this.props.onClose(cmd);
    } catch (err: any) {
      console.error(err);
      const message = errorHandlerApi.getErrorMessage(err);
      this.setState({
        invalidText: `ResponseError: ${message}`,
        updating: false,
      });
    }
  };

  handleDelete = () => {
    const { command } = this.props;
    let examples: Example[] = command.examples ?? [];
    const idx = this.props.idx!;
    examples = [...examples.slice(0, idx), ...examples.slice(idx + 1)];
    this.onUpdateExamples(examples);
  };

  handleModify = () => {
    const { command } = this.props;
    let { name, exampleCommands } = this.state;
    let examples: Example[] = command.examples ?? [];
    const idx = this.props.idx!;

    name = name.trim();
    if (name.length < 1) {
      this.setState({
        invalidText: `Field 'Name' is required.`,
      });
      return;
    }
    exampleCommands = exampleCommands
      .map((cmd) => {
        return cmd
          .split("\n")
          .map((cmdLine) => cmdLine.trim())
          .filter((cmdLine) => cmdLine.length > 0)
          .join(" ")
          .trim();
      })
      .filter((cmd) => cmd.length > 0);

    if (exampleCommands.length < 1) {
      this.setState({
        invalidText: `Field 'Commands' is required.`,
      });
      return;
    }

    const newExample: Example = {
      name: name,
      commands: exampleCommands,
    };

    examples = [...examples.slice(0, idx), newExample, ...examples.slice(idx + 1)];

    this.onUpdateExamples(examples);
  };

  handleAdd = () => {
    const { command } = this.props;
    let { name, exampleCommands } = this.state;
    const examples: Example[] = command.examples ?? [];

    name = name.trim();
    if (name.length < 1) {
      this.setState({
        invalidText: `Field 'Name' is required.`,
      });
      return;
    }
    exampleCommands = exampleCommands
      .map((cmd) => {
        return cmd
          .split("\n")
          .map((cmdLine) => cmdLine.trim())
          .filter((cmdLine) => cmdLine.length > 0)
          .join(" ")
          .trim();
      })
      .filter((cmd) => cmd.length > 0);

    if (exampleCommands.length < 1) {
      this.setState({
        invalidText: `Field 'Commands' is required.`,
      });
      return;
    }

    const newExample: Example = {
      name: name,
      commands: exampleCommands,
    };
    examples.push(newExample);

    this.onUpdateExamples(examples);
  };

  handleClose = () => {
    this.setState({
      invalidText: undefined,
    });
    this.props.onClose();
  };

  onModifyExampleCommand = (cmd: string, idx: number) => {
    this.setState((preState) => {
      return {
        ...preState,
        exampleCommands: [...preState.exampleCommands.slice(0, idx), cmd, ...preState.exampleCommands.slice(idx + 1)],
      };
    });
  };

  onRemoveExampleCommand = (idx: number) => {
    this.setState((preState) => {
      const exampleCommands: string[] = [
        ...preState.exampleCommands.slice(0, idx),
        ...preState.exampleCommands.slice(idx + 1),
      ];
      if (exampleCommands.length === 0) {
        exampleCommands.push("");
      }
      return {
        ...preState,
        exampleCommands: exampleCommands,
      };
    });
  };

  onAddExampleCommand = () => {
    this.setState((preState) => {
      return {
        ...preState,
        exampleCommands: [...preState.exampleCommands, ""],
      };
    });
  };

  loadSwaggerExamples = async () => {
    try {
      let { workspaceUrl, command } = this.props;

      const leafUrl =
        `${workspaceUrl}/CommandTree/Nodes/aaz/` +
        command.names.slice(0, -1).join("/") +
        "/Leaves/" +
        command.names[command.names.length - 1];

      this.setState({
        source: "swagger",
        updating: true,
      });
      const examples = await commandApi.generateSwaggerExamples(leafUrl);
      this.setState({
        exampleOptions: examples,
        updating: false,
      });
      if (examples.length > 0) {
        this.onExampleSelectorUpdate(examples[0].name);
      }
    } catch (err: any) {
      console.error(err.response);
      this.setState({
        updating: false,
        invalidText: errorHandlerApi.getErrorMessage(err),
      });
    }
  };

  onExampleSelectorUpdate = (exampleDisplayName: string | null) => {
    let example = this.state.exampleOptions.find((v) => v.name === exampleDisplayName) ?? undefined;

    if (example === undefined) {
      this.setState({
        name: exampleDisplayName ?? "",
      });
    } else {
      this.setState({
        name: example?.name ?? "",
        exampleCommands: example?.commands ?? [""],
      });
    }
  };

  render() {
    const { name, exampleCommands, isAdd, invalidText, updating, source, exampleOptions } = this.state;

    const selectedName = name;

    const buildExampleInput = (cmd: string, idx: number) => {
      return (
        <Box
          key={idx}
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "flex-start",
            ml: 1,
          }}
        >
          <IconButton edge="start" color="inherit" onClick={() => this.onRemoveExampleCommand(idx)} aria-label="remove">
            <DoDisturbOnRoundedIcon fontSize="small" />
          </IconButton>
          <Input
            id={`command-${idx}`}
            multiline
            value={cmd}
            onChange={(event: any) => {
              this.onModifyExampleCommand(event.target.value, idx);
            }}
            sx={{ flexGrow: 1 }}
            placeholder="Input a command here."
            startAdornment={
              <InputAdornment position="start">
                <ExampleCommandTypography>{COMMAND_PREFIX}</ExampleCommandTypography>
              </InputAdornment>
            }
          />
        </Box>
      );
    };

    return (
      <Dialog disableEscapeKeyDown open={this.props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
        <DialogTitle>
          {isAdd ? "Add Example" : "Modify Example"}
          <IconButton
            style={{ position: "absolute", right: 16, top: 8 }}
            edge="end"
            color="inherit"
            onClick={this.handleClose}
            aria-label="close"
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers={true}>
          {isAdd && source === undefined && (
            <Stack direction="column" spacing={2}>
              <Button
                variant="contained"
                size="large"
                color="secondary"
                sx={{ fontSize: "20px", padding: "10px 20px" }}
                onClick={() => {
                  this.loadSwaggerExamples();
                }}
              >
                <Typography variant="body2">By OpenAPI Specification</Typography>
              </Button>
            </Stack>
          )}
          {(!isAdd || source != undefined) && (
            <React.Fragment>
              {invalidText && (
                <Alert variant="filled" severity="error">
                  {" "}
                  {invalidText}{" "}
                </Alert>
              )}
              {!isAdd && (
                <React.Fragment>
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
                </React.Fragment>
              )}
              {source === "swagger" && (
                <React.Fragment>
                  <ExampleItemSelector
                    name="Name"
                    commonPrefix={""}
                    options={exampleOptions.map((v: any) => v.name)}
                    value={selectedName}
                    onValueUpdate={this.onExampleSelectorUpdate}
                  />
                </React.Fragment>
              )}
              <InputLabel required sx={{ font: "inherit", mt: 1 }}>
                Commands
              </InputLabel>
              {exampleCommands.map(buildExampleInput)}
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "center",
                  justifyContent: "flex-start",
                  ml: 1,
                }}
              >
                <IconButton edge="start" color="inherit" onClick={this.onAddExampleCommand} aria-label="add">
                  <AddCircleRoundedIcon fontSize="small" />
                </IconButton>
                <ExampleCommandTypography sx={{ flexShrink: 0 }}> One more command</ExampleCommandTypography>
              </Box>
            </React.Fragment>
          )}
        </DialogContent>
        {(!isAdd || source != undefined) && (
          <DialogActions>
            {updating && (
              <Box sx={{ width: "100%" }}>
                <LinearProgress color="secondary" />
              </Box>
            )}
            {!updating && (
              <React.Fragment>
                {!isAdd && (
                  <React.Fragment>
                    <Button onClick={this.handleDelete}>Delete</Button>
                    <Button onClick={this.handleModify}>Save</Button>
                  </React.Fragment>
                )}
                {isAdd && <Button onClick={this.handleAdd}>Add</Button>}
              </React.Fragment>
            )}
          </DialogActions>
        )}
      </Dialog>
    );
  }
}

export default ExampleDialog;
