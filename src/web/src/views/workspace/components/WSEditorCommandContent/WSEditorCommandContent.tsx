import {
  styled,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Accordion,
  LinearProgress,
  Typography,
  TypographyProps,
  AccordionDetails,
  AccordionSummaryProps,
} from "@mui/material";
import React, { useState, useEffect, useCallback, useRef } from "react";
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
} from "../WSEditor/WSEditorTheme";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import LabelIcon from "@mui/icons-material/Label";
import EditIcon from "@mui/icons-material/Edit";
import { commandApi } from "../../../../services";
import { COMMAND_PREFIX } from "../../../../constants";
import WSEditorCommandArgumentsContent from "../WSEditorCommandArgumentsContent";
import { DecodeResponseCommand } from "../../utils/decodeResponseCommand";
import ExampleDialog from "./ExampleDialog";
import AddSubcommandDialog from "./AddSubcommandDialog";
import CommandDeleteDialog from "./CommandDeleteDialog";
import CommandDialog from "./CommandDialog";
import OutputCard from "./OutputCard";
import OutputDialog from "./OutputDialog";
import type { Command, Example } from "../../interfaces";

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
  const lastLoadRef = useRef<string>("");

  useEffect(() => {
    const loadCommand = async () => {
      const requestKey = `${workspaceUrl}-${previewCommand.id}-${reloadTimestamp}`;

      if (lastLoadRef.current === requestKey) {
        return;
      }

      lastLoadRef.current = requestKey;
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
        }
      } catch (err: any) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (command?.id !== previewCommand.id) {
      setCommand(undefined);
    }
    loadCommand();
  }, [workspaceUrl, previewCommand.id, reloadTimestamp]);

  const reloadCommand = useCallback(async () => {
    lastLoadRef.current = "";
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
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [workspaceUrl, previewCommand.id, previewCommand.names]);

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
          {/* @TODO: update usage: */}
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
          onReloadArgs={reloadCommand}
          onAddSubCommand={onAddSubcommandDialogDisplay}
        />
      </Card>
    );
  }, [commandUrl, command, reloadCommand, onAddSubcommandDialogDisplay]);

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

export default WSEditorCommandContent;
