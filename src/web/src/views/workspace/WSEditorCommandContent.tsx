import {
  styled,
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Accordion,
  InputLabel,
  LinearProgress,
  Radio,
  RadioGroup,
  TextField,
  Typography,
  TypographyProps,
  AccordionDetails,
  AccordionSummaryProps,
  FormLabel,
  Switch,
  ButtonBase,
  FormLabelProps,
} from "@mui/material";
import React, { useState } from "react";
import MuiAccordionSummary from "@mui/material/AccordionSummary";
import {
  NameTypography,
  ShortHelpTypography,
  ShortHelpPlaceHolderTypography,
  LongHelpTypography,
  StableTypography,
  PreviewTypography,
  ExperimentalTypography,
  SubtitleTypography,
  CardTitleTypography,
} from "./WSEditorTheme";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import DataObjectIcon from "@mui/icons-material/DataObject";
import LabelIcon from "@mui/icons-material/Label";
import { commandApi, errorHandlerApi } from "../../services";
import { COMMAND_PREFIX } from "../../constants";
import WSEditorCommandArgumentsContent, {
  ClsArgDefinitionMap,
  CMDArg,
  DecodeArgs,
} from "./WSEditorCommandArgumentsContent";
import EditIcon from "@mui/icons-material/Edit";
import ExampleDialog from "./ExampleDialog";
import AddSubcommandDialog from "./AddSubcommandDialog";
import CommandDeleteDialog from "./CommandDeleteDialog";

interface Plane {
  name: string;
  displayName: string;
  moduleOptions?: string[];
}

interface Example {
  name: string;
  commands: string[];
}

interface ObjectOutput {
  type: "object";
  ref: string;
  clientFlatten: boolean;
}

interface ArrayOutput {
  type: "array";
  ref: string;
  clientFlatten: boolean;
  nextLink: string;
}

interface StringOutput {
  type: "string";
  ref: string;
  value: string;
}

type Output = ObjectOutput | ArrayOutput | StringOutput;

function isObjectOutput(output: Output): output is ObjectOutput {
  return output.type === "object";
}

function isArrayOutput(output: Output): output is ArrayOutput {
  return output.type === "array";
}

interface Resource {
  id: string;
  version: string;
  subresource?: string;
  swagger: string;
}

interface Command {
  id: string;
  names: string[];
  help?: {
    short: string;
    lines?: string[];
  };
  stage: "Stable" | "Preview" | "Experimental";
  version: string;
  examples?: Example[];
  outputs?: Output[];
  resources: Resource[];

  confirmation?: string;
  args?: CMDArg[];
  clsArgDefineMap?: ClsArgDefinitionMap;
}

interface ResponseCommand {
  names: string[];
  help?: {
    short: string;
    lines?: string[];
  };
  stage?: "Stable" | "Preview" | "Experimental";
  version: string;
  examples?: Example[];
  resources: Resource[];
  outputs?: Output[];
  confirmation?: string;
  argGroups?: any[];
}

interface ResponseCommands {
  [name: string]: ResponseCommand;
}

interface WSEditorCommandContentProps {
  workspaceUrl: string;
  previewCommand: Command;
  reloadTimestamp: number;
  onUpdateCommand: (command: Command | null) => void;
}

interface WSEditorCommandContentState {
  command?: Command;
  displayCommandDialog: boolean;
  displayExampleDialog: boolean;
  displayOutputDialog: boolean;
  displayCommandDeleteDialog: boolean;
  displayAddSubcommandDialog: boolean;
  subcommandDefaultGroupNames?: string[];
  subcommandArgVar?: string;
  subcommandSubArgOptions?: { var: string; options: string }[];
  exampleIdx?: number;
  outputIdx?: number;
  loading: boolean;
}

const ExampleCommandHeaderTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

const ExampleCommandBodyTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

const ExampleEditTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#5d64cf",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

const ExampleAccordionSummary = styled((props: AccordionSummaryProps) => (
  <MuiAccordionSummary expandIcon={<LabelIcon fontSize="small" color="primary" />} {...props} />
))(() => ({
  "flexDirection": "row-reverse",
  "& .MuiAccordionSummary-expandIconWrapper.Mui-expanded": {
    transform: "rotate(0deg)",
  },
}));

const OutputTypeTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 10,
  fontWeight: 400,
}));

const OutputRefTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 700,
}));

const OutputFlagTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#8888C3",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 10,
  fontWeight: 400,
}));

const OutputEditTypography = styled(Typography)<TypographyProps>(() => ({
  color: "#5d64cf",
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 14,
  fontWeight: 400,
}));

const OutputDialogLabel = styled(FormLabel)<FormLabelProps>(() => ({
  fontSize: 12,
}));

const OutputDialogMainTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 18,
  fontWeight: 400,
}));

class WSEditorCommandContent extends React.Component<WSEditorCommandContentProps, WSEditorCommandContentState> {
  constructor(props: WSEditorCommandContentProps) {
    super(props);
    this.state = {
      command: undefined,
      displayCommandDialog: false,
      displayExampleDialog: false,
      displayOutputDialog: false,
      displayCommandDeleteDialog: false,
      displayAddSubcommandDialog: false,
      loading: false,
    };
  }

  loadCommand = async () => {
    this.setState({ loading: true });
    const { workspaceUrl, previewCommand } = this.props;
    const commandNames = previewCommand.names;
    const leafUrl =
      `${workspaceUrl}/CommandTree/Nodes/aaz/` +
      commandNames.slice(0, -1).join("/") +
      "/Leaves/" +
      commandNames[commandNames.length - 1];
    try {
      const commandData = await commandApi.getCommand(leafUrl);
      const command = DecodeResponseCommand(commandData);
      if (command.id === this.props.previewCommand.id) {
        this.setState({
          loading: false,
          command: command,
        });
      }
    } catch (err: any) {
      this.setState({ loading: false });
      console.error(err);
      return;
    }
  };

  componentDidMount() {
    this.loadCommand();
  }

  componentDidUpdate(prevProps: WSEditorCommandContentProps) {
    if (
      prevProps.workspaceUrl !== this.props.workspaceUrl ||
      prevProps.previewCommand.id !== this.props.previewCommand.id ||
      prevProps.reloadTimestamp !== this.props.reloadTimestamp
    ) {
      if (prevProps.previewCommand.id !== this.props.previewCommand.id) {
        this.setState({ command: undefined });
      }
      this.loadCommand();
    }
  }

  onCommandDialogDisplay = () => {
    this.setState({
      displayCommandDialog: true,
    });
  };

  onCommandDeleteDialogDisplay = () => {
    this.setState({
      displayCommandDeleteDialog: true,
    });
  };

  handleCommandDialogClose = (newCommand?: Command) => {
    if (newCommand) {
      this.props.onUpdateCommand(newCommand!);
    }
    this.setState({
      displayCommandDialog: false,
    });
  };

  handleCommandDeleteDialogClose = (deleted: boolean) => {
    if (deleted) {
      this.props.onUpdateCommand(null);
    }
    this.setState({
      displayCommandDeleteDialog: false,
    });
  };

  onExampleDialogDisplay = (idx?: number) => {
    this.setState({
      displayExampleDialog: true,
      exampleIdx: idx,
    });
  };

  handleExampleDialogClose = (newCommand?: Command) => {
    if (newCommand) {
      this.props.onUpdateCommand(newCommand!);
    }
    this.setState({
      displayExampleDialog: false,
    });
  };

  onOutputDialogDisplay = (idx?: number) => {
    this.setState({
      displayOutputDialog: true,
      outputIdx: idx,
    });
  };

  handleOutputDialogClose = (newCommand?: Command) => {
    if (newCommand) {
      this.props.onUpdateCommand(newCommand!);
    }
    this.setState({
      displayOutputDialog: false,
    });
  };

  onAddSubcommandDialogDisplay = (
    argVar: string,
    subArgOptions: { var: string; options: string }[],
    argStackNames: string[],
  ) => {
    this.setState({
      displayAddSubcommandDialog: true,
      subcommandArgVar: argVar,
      subcommandSubArgOptions: subArgOptions,
      subcommandDefaultGroupNames: [...this.props.previewCommand.names.slice(0, -1), ...argStackNames],
    });
  };

  handleAddSubcommandDisplayClose = (add: boolean) => {
    if (add) {
      this.props.onUpdateCommand(this.state.command!);
    }
    this.setState({
      displayAddSubcommandDialog: false,
      subcommandArgVar: undefined,
      subcommandDefaultGroupNames: undefined,
    });
  };

  render() {
    const { workspaceUrl, previewCommand } = this.props;
    const commandNames = previewCommand.names;
    const name = COMMAND_PREFIX + commandNames.join(" ");
    const commandUrl =
      `${workspaceUrl}/CommandTree/Nodes/aaz/` +
      commandNames.slice(0, -1).join("/") +
      "/Leaves/" +
      commandNames[commandNames.length - 1];

    const {
      command,
      displayCommandDialog,
      displayExampleDialog,
      displayOutputDialog,
      displayCommandDeleteDialog,
      displayAddSubcommandDialog,
      exampleIdx,
      outputIdx,
      loading,
    } = this.state;

    const buildExampleView = (example: Example, idx: number) => {
      const buildCommand = (exampleCommand: string, cmdIdx: number) => {
        return (
          <Box
            key={`example-${idx}-command-${cmdIdx}`}
            sx={{
              display: "flex",
              flexDirection: "row",
              alignItems: "flex-start",
              justifyContent: "flex-start",
            }}
          >
            <Box
              component="span"
              sx={{
                flexShrink: 0,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "flex-start",
              }}
            >
              <KeyboardDoubleArrowRightIcon fontSize="small" />
              <ExampleCommandHeaderTypography sx={{ flexShrink: 0 }}>{COMMAND_PREFIX}</ExampleCommandHeaderTypography>
            </Box>
            <Box
              component="span"
              sx={{
                ml: 0.8,
              }}
            >
              <ExampleCommandBodyTypography>{exampleCommand}</ExampleCommandBodyTypography>
            </Box>
          </Box>
        );
      };
      return (
        <Accordion
          elevation={0}
          expanded
          key={`example-${idx}`}
          onDoubleClick={() => {
            this.onExampleDialogDisplay(idx);
          }}
        >
          <ExampleAccordionSummary id={`example-${idx}-header`}>
            <Box
              sx={{
                ml: 1,
                flexGrow: 1,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
              }}
            >
              <SubtitleTypography sx={{ flexShrink: 0 }}>{example.name}</SubtitleTypography>
              {/* <Box sx={{ flexGrow: 1 }} /> */}
              <Button
                sx={{ flexShrink: 0, ml: 3 }}
                startIcon={<EditIcon color="secondary" fontSize="small" />}
                onClick={() => {
                  this.onExampleDialogDisplay(idx);
                }}
              >
                <ExampleEditTypography>Edit</ExampleEditTypography>
              </Button>
            </Box>
          </ExampleAccordionSummary>
          <AccordionDetails
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "stretch",
              justifyContent: "flex-start",
              ml: 3,
              mr: 3,
              paddingTop: 0,
            }}
          >
            {example.commands.map(buildCommand)}
          </AccordionDetails>
        </Accordion>
      );
    };

    const buildCommandCard = () => {
      const shortHelp = (command ?? previewCommand).help?.short;
      const longHelp = (command ?? previewCommand).help?.lines?.join("\n");
      const lines: string[] = (command ?? previewCommand).help?.lines ?? [];
      const stage = (command ?? previewCommand).stage;
      const version = (command ?? previewCommand).version;

      return (
        <Card
          onDoubleClick={this.onCommandDialogDisplay}
          elevation={3}
          sx={{
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            p: 2,
          }}
        >
          <CardContent
            sx={{
              flex: "1 0 auto",
              display: "flex",
              flexDirection: "column",
              justifyContent: "stretch",
            }}
          >
            <Box
              sx={{
                mb: 2,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
              }}
            >
              <CardTitleTypography sx={{ flexShrink: 0 }}>[ COMMAND ]</CardTitleTypography>
              <Box sx={{ flexGrow: 1 }} />
              {stage === "Stable" && <StableTypography sx={{ flexShrink: 0 }}>{`v${version}`}</StableTypography>}
              {stage === "Preview" && <PreviewTypography sx={{ flexShrink: 0 }}>{`v${version}`}</PreviewTypography>}
              {stage === "Experimental" && (
                <ExperimentalTypography sx={{ flexShrink: 0 }}>{`v${version}`}</ExperimentalTypography>
              )}
            </Box>

            <NameTypography sx={{ mt: 1 }}>{name}</NameTypography>
            {shortHelp && <ShortHelpTypography sx={{ ml: 6, mt: 2 }}> {shortHelp} </ShortHelpTypography>}
            {!shortHelp && (
              <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>
                Please add command short summary!
              </ShortHelpPlaceHolderTypography>
            )}
            {longHelp && (
              <Box sx={{ ml: 6, mt: 1, mb: 1 }}>
                {lines.map((line, idx) => (
                  <LongHelpTypography key={idx}>{line}</LongHelpTypography>
                ))}
              </Box>
            )}
          </CardContent>
          <CardActions
            sx={{
              display: "flex",
              flexDirection: "row-reverse",
              alignContent: "center",
              justifyContent: "flex-start",
            }}
          >
            {loading && (
              <Box sx={{ width: "100%" }}>
                <LinearProgress color="secondary" />
              </Box>
            )}
            {!loading && (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  alignContent: "center",
                  justifyContent: "flex-start",
                }}
              >
                <Button
                  variant="contained"
                  size="small"
                  color="secondary"
                  disableElevation
                  onClick={this.onCommandDialogDisplay}
                  disabled={loading}
                  sx={{ mr: 2 }}
                >
                  <Typography variant="body2">Edit</Typography>
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  color="secondary"
                  onClick={this.onCommandDeleteDialogDisplay}
                  disabled={loading}
                  sx={{ mr: 2 }}
                >
                  <Typography variant="body2">Delete</Typography>
                </Button>
              </Box>
            )}
          </CardActions>
        </Card>
      );
    };

    const buildArgumentsCard = () => {
      return (
        <Card
          elevation={3}
          sx={{
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            mt: 1,
            p: 2,
          }}
        >
          <WSEditorCommandArgumentsContent
            commandUrl={commandUrl}
            args={command!.args!}
            clsArgDefineMap={command!.clsArgDefineMap!}
            onReloadArgs={this.loadCommand}
            onAddSubCommand={this.onAddSubcommandDialogDisplay}
          />
        </Card>
      );
    };

    const buildExampleCard = () => {
      const examples = command!.examples ?? [];
      return (
        <Card
          elevation={3}
          sx={{
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            mt: 1,
            p: 2,
          }}
        >
          <CardContent
            sx={{
              flex: "1 0 auto",
              display: "flex",
              flexDirection: "column",
              alignItems: "stretch",
            }}
          >
            <Box
              sx={{
                mb: 2,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
              }}
            >
              <CardTitleTypography sx={{ flexShrink: 0 }}>[ EXAMPLE ]</CardTitleTypography>
            </Box>
            {examples.length > 0 && <Box>{examples.map(buildExampleView)}</Box>}
          </CardContent>

          <CardActions
            sx={{
              display: "flex",
              flexDirection: "row-reverse",
            }}
          >
            <Button
              variant="contained"
              size="small"
              color="secondary"
              disableElevation
              onClick={() => this.onExampleDialogDisplay(undefined)}
            >
              <Typography variant="body2">Add</Typography>
            </Button>
          </CardActions>
        </Card>
      );
    };

    return (
      <React.Fragment>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "stretch",
          }}
        >
          {buildCommandCard()}
          {command !== undefined && command.args !== undefined && buildArgumentsCard()}
          {command !== undefined && buildExampleCard()}
          {command !== undefined && command.outputs !== undefined && (
            <OutputCard command={command} onOutputDialogDisplay={this.onOutputDialogDisplay} />
          )}
        </Box>
        {command !== undefined && displayCommandDialog && (
          <CommandDialog
            open={displayCommandDialog}
            workspaceUrl={workspaceUrl}
            command={command!}
            onClose={this.handleCommandDialogClose}
          />
        )}
        {command !== undefined && displayExampleDialog && (
          <ExampleDialog
            open={displayExampleDialog}
            workspaceUrl={workspaceUrl}
            command={command!}
            idx={exampleIdx}
            onClose={this.handleExampleDialogClose}
          />
        )}
        {command !== undefined && displayOutputDialog && (
          <OutputDialog
            open={displayOutputDialog}
            workspaceUrl={workspaceUrl}
            command={command!}
            idx={outputIdx}
            onClose={this.handleOutputDialogClose}
          />
        )}
        {command !== undefined && displayCommandDeleteDialog && (
          <CommandDeleteDialog
            open={displayCommandDeleteDialog}
            workspaceUrl={workspaceUrl}
            command={command!}
            onClose={this.handleCommandDeleteDialogClose}
          />
        )}
        {command !== undefined && displayAddSubcommandDialog && (
          <AddSubcommandDialog
            open={displayAddSubcommandDialog}
            workspaceUrl={workspaceUrl}
            command={command!}
            onClose={this.handleAddSubcommandDisplayClose}
            argVar={this.state.subcommandArgVar!}
            subArgOptions={this.state.subcommandSubArgOptions!}
            defaultGroupNames={this.state.subcommandDefaultGroupNames!}
          />
        )}
      </React.Fragment>
    );
  }
}

interface CommandDialogProps {
  workspaceUrl: string;
  open: boolean;
  command: Command;
  onClose: (newCommand?: Command) => void;
}

interface CommandDialogState {
  name: string;
  stage: string;
  shortHelp: string;
  longHelp: string;
  invalidText?: string;
  confirmation: string;
  updating: boolean;
}

class CommandDialog extends React.Component<CommandDialogProps, CommandDialogState> {
  constructor(props: CommandDialogProps) {
    super(props);
    this.state = {
      name: this.props.command.names.join(" "),
      shortHelp: this.props.command.help?.short ?? "",
      longHelp: this.props.command.help?.lines?.join("\n") ?? "",
      stage: this.props.command.stage,
      confirmation: this.props.command.confirmation ?? "",
      updating: false,
    };
  }

  handleModify = async () => {
    let { name, shortHelp, longHelp, confirmation } = this.state;
    const { stage } = this.state;

    const { workspaceUrl, command } = this.props;

    name = name.trim();
    shortHelp = shortHelp.trim();
    longHelp = longHelp.trim();
    confirmation = confirmation.trim();

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
      return;
    }

    let lines: string[] | null = null;
    if (longHelp.length > 1) {
      lines = longHelp.split("\n").filter((l) => l.length > 0);
    }

    this.setState({
      updating: true,
    });

    const leafUrl =
      `${workspaceUrl}/CommandTree/Nodes/aaz/` +
      command.names.slice(0, -1).join("/") +
      "/Leaves/" +
      command.names[command.names.length - 1];

    try {
      const commandData = await commandApi.updateCommand(leafUrl, {
        help: {
          short: shortHelp,
          lines: lines,
        },
        stage: stage,
        confirmation: confirmation,
      });

      const name = names.join(" ");
      if (name === command.names.join(" ")) {
        const cmd = DecodeResponseCommand(commandData);
        this.setState({
          updating: false,
        });
        this.props.onClose(cmd);
      } else {
        const renamedData = await commandApi.renameCommand(leafUrl, name);
        const cmd = DecodeResponseCommand(renamedData);
        this.setState({
          updating: false,
        });
        this.props.onClose(cmd);
      }
    } catch (err: any) {
      console.error(err);
      this.setState({
        invalidText: errorHandlerApi.getErrorMessage(err),
        updating: false,
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
    const { name, shortHelp, longHelp, invalidText, updating, stage, confirmation } = this.state;
    return (
      <Dialog disableEscapeKeyDown open={this.props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
        <DialogTitle>Command</DialogTitle>
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
          <TextField
            id="confirmation"
            label="Command confirmation"
            helperText="Modify or clear confirmation message as needed."
            type="text"
            fullWidth
            multiline
            variant="standard"
            value={confirmation}
            onChange={(event: any) => {
              this.setState({
                confirmation: event.target.value,
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

function OutputCard(props: { command: Command; onOutputDialogDisplay: (idx: number) => void }) {
  const outputs = props.command!.outputs!;

  const buildBaseOutputView = (
    idx: number,
    refName: string,
    type: string,
    flags: string[],
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    return (
      <Box sx={{ my: 1 }}>
        <Box
          sx={{
            p: 2,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
          }}
        >
          <DataObjectIcon fontSize="small" />
          <SubtitleTypography sx={{ ml: 1 }}>JSON</SubtitleTypography>
          <Button
            sx={{ flexShrink: 0, ml: 3 }}
            startIcon={<EditIcon color="secondary" fontSize="small" />}
            onClick={onClick}
          >
            <OutputEditTypography>Edit</OutputEditTypography>
          </Button>
        </Box>
        <Box
          key={`output-${idx}-${refName}`}
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "stretch",
            justifyContent: "flex-start",
            mb: 2,
            ml: 6,
          }}
        >
          <Box>
            <ButtonBase onClick={onClick}>
              <OutputRefTypography>{refName}</OutputRefTypography>
            </ButtonBase>
          </Box>
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
              alignItems: "flex-start",
              justifyContent: "flex-start",
            }}
          >
            <Box
              sx={{
                width: 300,
                flexShrink: 0,
                flexDirection: "row",
                display: "flex",
                alignItems: "center",
              }}
            >
              <OutputTypeTypography
                sx={{
                  flexShrink: 0,
                }}
              >{`/${type}/`}</OutputTypeTypography>
              <Box sx={{ flexGrow: 1 }} />
              {flags.map((flag, idx) => {
                return <OutputFlagTypography key={`output-flag-${idx}`}>{`[${flag}]`}</OutputFlagTypography>;
              })}
            </Box>
          </Box>
        </Box>
      </Box>
    );
  };

  const buildObjectOutputView = (
    output: ObjectOutput,
    idx: number,
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    return buildBaseOutputView(
      idx,
      output.ref,
      output.type,
      output.clientFlatten ? ["Flattened"] : ["Unflattened"],
      onClick,
    );
  };

  const buildArrayOutputView = (
    output: ArrayOutput,
    idx: number,
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    return buildBaseOutputView(
      idx,
      output.ref,
      output.type,
      output.clientFlatten ? ["Flattened"] : ["Unflattened"],
      onClick,
    );
  };

  const buildStringOutputView = (
    output: StringOutput,
    idx: number,
    onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined,
  ) => {
    const title = output.ref ? output.ref : output.value;
    return buildBaseOutputView(idx, title, output.type, [], onClick);
  };

  const buildOutputView = (output: Output, idx: number) => {
    const onClick = () => {
      props.onOutputDialogDisplay(idx);
    };
    switch (output.type) {
      case "object":
        return buildObjectOutputView(output, idx, onClick);
      case "array":
        return buildArrayOutputView(output, idx, onClick);
      case "string":
        return buildStringOutputView(output, idx, onClick);
    }
  };

  return (
    <Card
      elevation={3}
      sx={{
        flexGrow: 1,
        display: "flex",
        flexDirection: "column",
        mt: 1,
        p: 2,
      }}
    >
      <CardContent
        sx={{
          flex: "1 0 auto",
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
        }}
      >
        <Box
          sx={{
            mb: 2,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
          }}
        >
          <CardTitleTypography sx={{ flexShrink: 0 }}>[ OUTPUT ]</CardTitleTypography>
        </Box>
        {outputs.length > 0 && outputs.map(buildOutputView)}
      </CardContent>
    </Card>
  );
}

function OutputDialog(props: {
  workspaceUrl: string;
  command: Command;
  idx?: number;
  open: boolean;
  onClose: (newCommand?: Command) => void;
}) {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const outputs = props.command.outputs ?? [];
  const output = outputs[props.idx!];
  const [flatten, setFlatten] = useState<boolean>(output.type !== "string" ? output.clientFlatten : false);
  const flattenLabelContent = flatten ? "Flattened" : "Unflattened";

  const handleClose = () => {
    setInvalidText(undefined);
    props.onClose();
  };

  const handleUpdateOutput = async () => {
    setInvalidText(undefined);
    setUpdating(true);

    if (isObjectOutput(output) || isArrayOutput(output)) {
      let commandNames = props.command.names;
      const leafUrl =
        `${props.workspaceUrl}/CommandTree/Nodes/aaz/` +
        commandNames.slice(0, -1).join("/") +
        "/Leaves/" +
        commandNames[commandNames.length - 1];
      console.log("Original clientFlatten: ");
      console.log(output.clientFlatten);
      output.clientFlatten = !output.clientFlatten;
      console.log("New clientFlatten: ");
      console.log(output.clientFlatten);

      try {
        const responseData = await commandApi.updateCommandOutputs(leafUrl, outputs);
        const cmd = DecodeResponseCommand(responseData);
        setUpdating(false);
        props.onClose(cmd);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
        setUpdating(false);
      }
    } else {
      console.error(`Invalid output type for flatten switch: ${output.type}`);
      setInvalidText(`Invalid output type for flatten switch: ${output.type}`);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      <DialogTitle>JSON Format Output</DialogTitle>
      <DialogContent dividers={true}>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        {(output.type !== "string" || output.ref !== undefined) && (
          <React.Fragment>
            <OutputDialogLabel>Output Reference</OutputDialogLabel>
            <OutputDialogMainTypography sx={{ my: 1 }}>{output.ref}</OutputDialogMainTypography>
          </React.Fragment>
        )}
        {output.type == "string" && output.ref == undefined && (
          <React.Fragment>
            <OutputDialogLabel>Output Value</OutputDialogLabel>
            <OutputDialogMainTypography sx={{ my: 1 }}>{output.value}</OutputDialogMainTypography>
          </React.Fragment>
        )}
        {output.type == "array" && output.nextLink !== undefined && (
          <React.Fragment>
            <OutputDialogLabel>Next Link Reference</OutputDialogLabel>
            <OutputDialogMainTypography sx={{ my: 1 }}>{output.nextLink}</OutputDialogMainTypography>
          </React.Fragment>
        )}
        {(output.type !== "string" || output.ref !== undefined) && (
          <React.Fragment>
            <OutputDialogLabel>Client Flatten</OutputDialogLabel>
            <Box sx={{ display: "flex" }}>
              <FormControlLabel
                sx={{ ml: 2 }}
                control={
                  <Switch
                    checked={flatten}
                    onChange={(event: any) => {
                      setFlatten(event.target.checked);
                    }}
                  />
                }
                label={<OutputDialogMainTypography sx={{ mx: 2 }}>{flattenLabelContent}</OutputDialogMainTypography>}
                labelPlacement="end"
              />
            </Box>
          </React.Fragment>
        )}
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && <Button onClick={handleClose}>Cancel</Button>}
        <Button onClick={handleUpdateOutput}>Update</Button>
      </DialogActions>
    </Dialog>
  );
}

const DecodeResponseCommand = (command: ResponseCommand): Command => {
  let cmd: Command = {
    id: "command:" + command.names.join("/"),
    names: command.names,
    help: command.help,
    stage: command.stage ?? "Stable",
    examples: command.examples,
    outputs: command.outputs,
    resources: command.resources,
    version: command.version,
  };

  if (command.confirmation) {
    cmd.confirmation = command.confirmation;
  }

  if (command.argGroups) {
    cmd = {
      ...cmd,
      ...DecodeArgs(command.argGroups!),
    };
  }

  return cmd;
};

export default WSEditorCommandContent;

export { DecodeResponseCommand };

export type { Plane, Command, Resource, ResponseCommand, ResponseCommands, Example };
