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
} from "@mui/material";
import React, { useState, useEffect, useCallback } from "react";
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
} from "../WSEditorTheme";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import LabelIcon from "@mui/icons-material/Label";
import EditIcon from "@mui/icons-material/Edit";
import { commandApi, errorHandlerApi } from "../../../services";
import { COMMAND_PREFIX } from "../../../constants";
import WSEditorCommandArgumentsContent, { ClsArgDefinitionMap, CMDArg, DecodeArgs } from "../commandArgumentsContent";
import ExampleDialog from "./ExampleDialog";
import AddSubcommandDialog from "./AddSubcommandDialog";
import CommandDeleteDialog from "./CommandDeleteDialog";
import OutputCard from "./OutputCard";
import OutputDialog, { Output } from "./OutputDialog";

interface Plane {
  name: string;
  displayName: string;
  moduleOptions?: string[];
}

interface Example {
  name: string;
  commands: string[];
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

const WSEditorCommandContent: React.FC<WSEditorCommandContentProps> = ({
  workspaceUrl,
  previewCommand,
  reloadTimestamp,
  onUpdateCommand,
}) => {
  const [command, setCommand] = useState<Command | undefined>(undefined);
  const [displayCommandDialog, setDisplayCommandDialog] = useState(false);
  const [displayExampleDialog, setDisplayExampleDialog] = useState(false);
  const [displayOutputDialog, setDisplayOutputDialog] = useState(false);
  const [displayCommandDeleteDialog, setDisplayCommandDeleteDialog] = useState(false);
  const [displayAddSubcommandDialog, setDisplayAddSubcommandDialog] = useState(false);
  const [subcommandDefaultGroupNames, setSubcommandDefaultGroupNames] = useState<string[] | undefined>(undefined);
  const [subcommandArgVar, setSubcommandArgVar] = useState<string | undefined>(undefined);
  const [subcommandSubArgOptions, setSubcommandSubArgOptions] = useState<
    { var: string; options: string }[] | undefined
  >(undefined);
  const [exampleIdx, setExampleIdx] = useState<number | undefined>(undefined);
  const [outputIdx, setOutputIdx] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const loadCommand = useCallback(async () => {
    setLoading(true);
    const commandNames = previewCommand.names;
    const leafUrl =
      `${workspaceUrl}/CommandTree/Nodes/aaz/` +
      commandNames.slice(0, -1).join("/") +
      "/Leaves/" +
      commandNames[commandNames.length - 1];
    try {
      const commandData = await commandApi.getCommand(leafUrl);
      const cmd = DecodeResponseCommand(commandData);
      if (cmd.id === previewCommand.id) {
        setCommand(cmd);
        setLoading(false);
      }
    } catch (err: any) {
      setLoading(false);
      console.error(err);
      return;
    }
  }, [workspaceUrl, previewCommand]);

  useEffect(() => {
    loadCommand();
  }, [loadCommand]);

  useEffect(() => {
    if (command?.id !== previewCommand.id) {
      setCommand(undefined);
    }
    loadCommand();
  }, [workspaceUrl, previewCommand.id, reloadTimestamp, loadCommand, command?.id, previewCommand]);

  const onCommandDialogDisplay = useCallback(() => {
    setDisplayCommandDialog(true);
  }, []);

  const onCommandDeleteDialogDisplay = useCallback(() => {
    setDisplayCommandDeleteDialog(true);
  }, []);

  const handleCommandDialogClose = useCallback(
    (newCommand?: Command) => {
      if (newCommand) {
        onUpdateCommand(newCommand);
      }
      setDisplayCommandDialog(false);
    },
    [onUpdateCommand],
  );

  const handleCommandDeleteDialogClose = useCallback(
    (deleted: boolean) => {
      if (deleted) {
        onUpdateCommand(null);
      }
      setDisplayCommandDeleteDialog(false);
    },
    [onUpdateCommand],
  );

  const onExampleDialogDisplay = useCallback((idx?: number) => {
    setDisplayExampleDialog(true);
    setExampleIdx(idx);
  }, []);

  const handleExampleDialogClose = useCallback(
    (newCommand?: Command) => {
      if (newCommand) {
        onUpdateCommand(newCommand);
      }
      setDisplayExampleDialog(false);
    },
    [onUpdateCommand],
  );

  const onOutputDialogDisplay = useCallback((idx?: number) => {
    setDisplayOutputDialog(true);
    setOutputIdx(idx);
  }, []);

  const handleOutputDialogClose = useCallback(
    (newCommand?: Command) => {
      if (newCommand) {
        onUpdateCommand(newCommand);
      }
      setDisplayOutputDialog(false);
    },
    [onUpdateCommand],
  );

  const onAddSubcommandDialogDisplay = useCallback(
    (argVar: string, subArgOptions: { var: string; options: string }[], argStackNames: string[]) => {
      setDisplayAddSubcommandDialog(true);
      setSubcommandArgVar(argVar);
      setSubcommandSubArgOptions(subArgOptions);
      setSubcommandDefaultGroupNames([...previewCommand.names.slice(0, -1), ...argStackNames]);
    },
    [previewCommand.names],
  );

  const handleAddSubcommandDisplayClose = useCallback(
    (add: boolean) => {
      if (add && command) {
        onUpdateCommand(command);
      }
      setDisplayAddSubcommandDialog(false);
      setSubcommandArgVar(undefined);
      setSubcommandDefaultGroupNames(undefined);
    },
    [command, onUpdateCommand],
  );

  const commandNames = previewCommand.names;
  const name = COMMAND_PREFIX + commandNames.join(" ");
  const commandUrl =
    `${workspaceUrl}/CommandTree/Nodes/aaz/` +
    commandNames.slice(0, -1).join("/") +
    "/Leaves/" +
    commandNames[commandNames.length - 1];

  const buildExampleView = useCallback(
    (example: Example, idx: number) => {
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
            onExampleDialogDisplay(idx);
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
              <Button
                sx={{ flexShrink: 0, ml: 3 }}
                startIcon={<EditIcon color="secondary" fontSize="small" />}
                onClick={() => {
                  onExampleDialogDisplay(idx);
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
    },
    [onExampleDialogDisplay],
  );

  const buildCommandCard = useCallback(() => {
    const shortHelp = (command ?? previewCommand).help?.short;
    const longHelp = (command ?? previewCommand).help?.lines?.join("\n");
    const stage = (command ?? previewCommand).stage;
    const version = (command ?? previewCommand).version;

    return (
      <Card
        onDoubleClick={onCommandDialogDisplay}
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
              {longHelp
                .split("\n")
                .filter((l) => l.length > 0)
                .map((line, idx) => (
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
                data-testid="update-command"
                variant="contained"
                size="small"
                color="secondary"
                disableElevation
                onClick={onCommandDialogDisplay}
                disabled={loading}
                sx={{ mr: 2 }}
              >
                <Typography variant="body2">Edit</Typography>
              </Button>
              <Button
                variant="outlined"
                size="small"
                color="secondary"
                onClick={onCommandDeleteDialogDisplay}
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
  }, [command, previewCommand, name, onCommandDialogDisplay, loading, onCommandDeleteDialogDisplay]);
  const buildArgumentsCard = useCallback(() => {
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
          onReloadArgs={loadCommand}
          onAddSubCommand={onAddSubcommandDialogDisplay}
        />
      </Card>
    );
  }, [commandUrl, command, loadCommand, onAddSubcommandDialogDisplay]);

  const buildExampleCard = useCallback(() => {
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
            onClick={() => onExampleDialogDisplay(undefined)}
          >
            <Typography variant="body2">Add</Typography>
          </Button>
        </CardActions>
      </Card>
    );
  }, [command, buildExampleView, onExampleDialogDisplay]);

  return (
    <React.Fragment>
      <Box
        data-testid="ws-editor-command-content"
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
          <OutputCard command={command} onOutputDialogDisplay={onOutputDialogDisplay} />
        )}
      </Box>
      {command !== undefined && displayCommandDialog && (
        <CommandDialog
          open={displayCommandDialog}
          workspaceUrl={workspaceUrl}
          command={command}
          onClose={handleCommandDialogClose}
        />
      )}
      {command !== undefined && displayExampleDialog && (
        <ExampleDialog
          open={displayExampleDialog}
          workspaceUrl={workspaceUrl}
          command={command}
          idx={exampleIdx}
          onClose={handleExampleDialogClose}
        />
      )}
      {command !== undefined && displayOutputDialog && (
        <OutputDialog
          open={displayOutputDialog}
          workspaceUrl={workspaceUrl}
          command={command}
          idx={outputIdx}
          onClose={handleOutputDialogClose}
        />
      )}
      {command !== undefined && displayCommandDeleteDialog && (
        <CommandDeleteDialog
          open={displayCommandDeleteDialog}
          workspaceUrl={workspaceUrl}
          command={command}
          onClose={handleCommandDeleteDialogClose}
        />
      )}
      {command !== undefined && displayAddSubcommandDialog && (
        <AddSubcommandDialog
          open={displayAddSubcommandDialog}
          workspaceUrl={workspaceUrl}
          command={command}
          onClose={handleAddSubcommandDisplayClose}
          argVar={subcommandArgVar!}
          subArgOptions={subcommandSubArgOptions!}
          defaultGroupNames={subcommandDefaultGroupNames!}
        />
      )}
    </React.Fragment>
  );
};

interface CommandDialogProps {
  workspaceUrl: string;
  open: boolean;
  command: Command;
  onClose: (newCommand?: Command) => void;
}

const CommandDialog: React.FC<CommandDialogProps> = ({ workspaceUrl, open, command, onClose }) => {
  const [name, setName] = useState(command.names.join(" "));
  const [shortHelp, setShortHelp] = useState(command.help?.short ?? "");
  const [longHelp, setLongHelp] = useState(command.help?.lines?.join("\n") ?? "");
  const [stage, setStage] = useState(command.stage);
  const [confirmation, setConfirmation] = useState(command.confirmation ?? "");
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [updating, setUpdating] = useState(false);

  const handleModify = useCallback(async () => {
    let trimmedName = name.trim();
    let trimmedShortHelp = shortHelp.trim();
    let trimmedLongHelp = longHelp.trim();
    let trimmedConfirmation = confirmation.trim();

    const names = trimmedName.split(" ").filter((n) => n.length > 0);

    setInvalidText(undefined);

    if (names.length < 1) {
      setInvalidText(`Field 'Name' is required.`);
      return;
    }

    for (const idx in names) {
      const piece = names[idx];
      if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
        setInvalidText(`Invalid Name part: '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `);
        return;
      }
    }

    if (trimmedShortHelp.length < 1) {
      setInvalidText(`Field 'Short Summary' is required.`);
      return;
    }

    let lines: string[] | null = null;
    if (trimmedLongHelp.length > 1) {
      lines = trimmedLongHelp.split("\n").filter((l) => l.length > 0);
    }

    setUpdating(true);

    const leafUrl =
      `${workspaceUrl}/CommandTree/Nodes/aaz/` +
      command.names.slice(0, -1).join("/") +
      "/Leaves/" +
      command.names[command.names.length - 1];

    try {
      const commandData = await commandApi.updateCommand(leafUrl, {
        help: {
          short: trimmedShortHelp,
          lines: lines,
        },
        stage: stage,
        confirmation: trimmedConfirmation,
      });

      const commandName = names.join(" ");
      if (commandName === command.names.join(" ")) {
        const cmd = DecodeResponseCommand(commandData);
        setUpdating(false);
        onClose(cmd);
      } else {
        const renamedData = await commandApi.renameCommand(leafUrl, commandName);
        const cmd = DecodeResponseCommand(renamedData);
        setUpdating(false);
        onClose(cmd);
      }
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  }, [name, shortHelp, longHelp, confirmation, stage, workspaceUrl, command, onClose]);

  const handleClose = useCallback(() => {
    setInvalidText(undefined);
    onClose();
  }, [onClose]);

  return (
    <Dialog disableEscapeKeyDown open={open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
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
            setStage(event.target.value);
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
            setName(event.target.value);
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
            setShortHelp(event.target.value);
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
            setLongHelp(event.target.value);
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
            setConfirmation(event.target.value);
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
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleModify}>Save</Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

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
