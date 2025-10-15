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
import React, { useState, useCallback, useEffect } from "react";
import DoDisturbOnRoundedIcon from "@mui/icons-material/DoDisturbOnRounded";
import AddCircleRoundedIcon from "@mui/icons-material/AddCircleRounded";
import CloseIcon from "@mui/icons-material/Close";
import { commandApi, errorHandlerApi } from "../../../services";
import { COMMAND_PREFIX } from "../../../constants";
import { ExampleItemSelector } from "../WSEditorExamplePicker";
import { DecodeResponseCommand } from "../utils/decodeResponseCommand";
import type { Command, Example } from "../interfaces";

export interface ExampleDialogProps {
  workspaceUrl: string;
  open: boolean;
  command: Command;
  idx?: number;
  onClose: (newCommand?: Command) => void;
}

const ExampleCommandTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Roboto Condensed', sans-serif",
  fontSize: 16,
  fontWeight: 400,
}));

const ExampleDialog: React.FC<ExampleDialogProps> = ({ workspaceUrl, open, command, idx, onClose }) => {
  const [name, setName] = useState<string>("");
  const [exampleCommands, setExampleCommands] = useState<string[]>([""]);
  const [isAdd, setIsAdd] = useState<boolean>(true);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [updating, setUpdating] = useState<boolean>(false);
  const [source, setSource] = useState<string | undefined>(undefined);
  const [exampleOptions, setExampleOptions] = useState<Example[]>([]);

  useEffect(() => {
    const examples: Example[] = command.examples ?? [];
    if (idx === undefined) {
      setName("");
      setExampleCommands([""]);
      setIsAdd(true);
      setInvalidText(undefined);
      setUpdating(false);
      setSource(undefined);
      setExampleOptions([]);
    } else {
      const example = examples[idx];
      setName(example.name);
      setExampleCommands(example.commands);
      setIsAdd(false);
      setInvalidText(undefined);
      setUpdating(false);
      setSource(undefined);
      setExampleOptions([]);
    }
  }, [command.examples, idx]);

  const onUpdateExamples = useCallback(
    async (examples: Example[]) => {
      const leafUrl =
        `${workspaceUrl}/CommandTree/Nodes/aaz/` +
        command.names.slice(0, -1).join("/") +
        "/Leaves/" +
        command.names[command.names.length - 1];

      setUpdating(true);

      try {
        const responseData = await commandApi.updateCommandExamples(leafUrl, examples);
        const cmd = DecodeResponseCommand(responseData);
        setUpdating(false);
        onClose(cmd);
      } catch (err: any) {
        console.error(err);
        const message = errorHandlerApi.getErrorMessage(err);
        setInvalidText(`ResponseError: ${message}`);
        setUpdating(false);
      }
    },
    [workspaceUrl, command.names, onClose],
  );

  const handleDelete = useCallback(() => {
    let examples: Example[] = command.examples ?? [];
    const currentIdx = idx!;
    examples = [...examples.slice(0, currentIdx), ...examples.slice(currentIdx + 1)];
    onUpdateExamples(examples);
  }, [command.examples, idx, onUpdateExamples]);

  const handleModify = useCallback(() => {
    let trimmedName = name.trim();
    let examples: Example[] = command.examples ?? [];
    const currentIdx = idx!;

    if (trimmedName.length < 1) {
      setInvalidText(`Field 'Name' is required.`);
      return;
    }

    const processedCommands = exampleCommands
      .map((cmd) => {
        return cmd
          .split("\n")
          .map((cmdLine) => cmdLine.trim())
          .filter((cmdLine) => cmdLine.length > 0)
          .join(" ")
          .trim();
      })
      .filter((cmd) => cmd.length > 0);

    if (processedCommands.length < 1) {
      setInvalidText(`Field 'Commands' is required.`);
      return;
    }

    const newExample: Example = {
      name: trimmedName,
      commands: processedCommands,
    };

    examples = [...examples.slice(0, currentIdx), newExample, ...examples.slice(currentIdx + 1)];
    onUpdateExamples(examples);
  }, [name, exampleCommands, command.examples, idx, onUpdateExamples]);

  const handleAdd = useCallback(() => {
    let trimmedName = name.trim();
    const examples: Example[] = command.examples ?? [];

    if (trimmedName.length < 1) {
      setInvalidText(`Field 'Name' is required.`);
      return;
    }

    const processedCommands = exampleCommands
      .map((cmd) => {
        return cmd
          .split("\n")
          .map((cmdLine) => cmdLine.trim())
          .filter((cmdLine) => cmdLine.length > 0)
          .join(" ")
          .trim();
      })
      .filter((cmd) => cmd.length > 0);

    if (processedCommands.length < 1) {
      setInvalidText(`Field 'Commands' is required.`);
      return;
    }

    const newExample: Example = {
      name: trimmedName,
      commands: processedCommands,
    };
    examples.push(newExample);
    onUpdateExamples(examples);
  }, [name, exampleCommands, command.examples, onUpdateExamples]);

  const handleClose = useCallback(() => {
    setInvalidText(undefined);
    onClose();
  }, [onClose]);

  const onModifyExampleCommand = useCallback((cmd: string, cmdIdx: number) => {
    setExampleCommands((prevCommands) => [...prevCommands.slice(0, cmdIdx), cmd, ...prevCommands.slice(cmdIdx + 1)]);
  }, []);

  const onRemoveExampleCommand = useCallback((cmdIdx: number) => {
    setExampleCommands((prevCommands) => {
      const newCommands = [...prevCommands.slice(0, cmdIdx), ...prevCommands.slice(cmdIdx + 1)];
      if (newCommands.length === 0) {
        newCommands.push("");
      }
      return newCommands;
    });
  }, []);

  const onAddExampleCommand = useCallback(() => {
    setExampleCommands((prevCommands) => [...prevCommands, ""]);
  }, []);

  const loadSwaggerExamples = useCallback(async () => {
    try {
      const leafUrl =
        `${workspaceUrl}/CommandTree/Nodes/aaz/` +
        command.names.slice(0, -1).join("/") +
        "/Leaves/" +
        command.names[command.names.length - 1];

      setSource("swagger");
      setUpdating(true);
      const examples = await commandApi.generateSwaggerExamples(leafUrl);
      setExampleOptions(examples);
      setUpdating(false);
      if (examples.length > 0) {
        onExampleSelectorUpdate(examples[0].name);
      }
    } catch (err: any) {
      console.error(err.response);
      setUpdating(false);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
    }
  }, [workspaceUrl, command.names]);

  const onExampleSelectorUpdate = useCallback(
    (exampleDisplayName: string | null) => {
      const example = exampleOptions.find((v) => v.name === exampleDisplayName) ?? undefined;

      if (example === undefined) {
        setName(exampleDisplayName ?? "");
      } else {
        setName(example?.name ?? "");
        setExampleCommands(example?.commands ?? [""]);
      }
    },
    [exampleOptions],
  );

  const buildExampleInput = useCallback(
    (cmd: string, cmdIdx: number) => {
      return (
        <Box
          key={cmdIdx}
          sx={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "flex-start",
            ml: 1,
          }}
        >
          <IconButton edge="start" color="inherit" onClick={() => onRemoveExampleCommand(cmdIdx)} aria-label="remove">
            <DoDisturbOnRoundedIcon fontSize="small" />
          </IconButton>
          <Input
            id={`command-${cmdIdx}`}
            multiline
            value={cmd}
            onChange={(event: any) => {
              onModifyExampleCommand(event.target.value, cmdIdx);
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
    },
    [onRemoveExampleCommand, onModifyExampleCommand],
  );

  const selectedName = name;

  return (
    <Dialog disableEscapeKeyDown open={open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      <DialogTitle>
        {isAdd ? "Add Example" : "Modify Example"}
        <IconButton
          style={{ position: "absolute", right: 16, top: 8 }}
          edge="end"
          color="inherit"
          onClick={handleClose}
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
              onClick={loadSwaggerExamples}
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
                    setName(event.target.value);
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
                  onValueUpdate={onExampleSelectorUpdate}
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
              <IconButton edge="start" color="inherit" onClick={onAddExampleCommand} aria-label="add">
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
                  <Button onClick={handleDelete}>Delete</Button>
                  <Button onClick={handleModify}>Save</Button>
                </React.Fragment>
              )}
              {isAdd && <Button onClick={handleAdd}>Add</Button>}
            </React.Fragment>
          )}
        </DialogActions>
      )}
    </Dialog>
  );
};

export default ExampleDialog;
