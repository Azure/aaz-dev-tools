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
import React, { useState, useCallback } from "react";
import { commandApi, errorHandlerApi } from "../../../../services";
import { DecodeResponseCommand } from "../../utils/decodeResponseCommand";
import type { Command } from "../../interfaces";

export interface CommandDialogProps {
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

export default CommandDialog;
