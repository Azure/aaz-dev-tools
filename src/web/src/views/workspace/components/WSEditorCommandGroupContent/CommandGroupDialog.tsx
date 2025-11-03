import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  InputLabel,
  Radio,
  RadioGroup,
  TextField,
} from "@mui/material";
import { commandApi, errorHandlerApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import { AsyncOperationBanner } from "../../../../components";
import * as React from "react";
import { DecodeResponseCommandGroup } from "./WSEditorCommandGroupContent";
import type { CommandGroup } from "../../interfaces";

interface CommandGroupDialogProps {
  workspaceUrl: string;
  open: boolean;
  commandGroup: CommandGroup;
  onClose: (newCommandGroup?: CommandGroup) => void;
}

const CommandGroupDialog: React.FC<CommandGroupDialogProps> = ({ workspaceUrl, open, commandGroup, onClose }) => {
  const [name, setName] = React.useState<string>(commandGroup.names.join(" "));
  const [stage, setStage] = React.useState<string>(commandGroup.stage);
  const [shortHelp, setShortHelp] = React.useState<string>(commandGroup.help?.short ?? "");
  const [longHelp, setLongHelp] = React.useState<string>(commandGroup.help?.lines?.join("\n") ?? "");
  const [invalidText, setInvalidText] = React.useState<string | undefined>(undefined);

  const updateCommandGroupOperation = useAsyncOperation(commandApi.updateCommandGroup);
  const renameCommandGroupOperation = useAsyncOperation(commandApi.renameCommandGroup);

  React.useEffect(() => {
    setName(commandGroup.names.join(" "));
    setStage(commandGroup.stage);
    setShortHelp(commandGroup.help?.short ?? "");
    setLongHelp(commandGroup.help?.lines?.join("\n") ?? "");
    setInvalidText(undefined);
  }, [commandGroup]);

  const handleModify = React.useCallback(async () => {
    let trimmedName = name.trim();
    let trimmedShortHelp = shortHelp.trim();
    let trimmedLongHelp = longHelp.trim();

    const names = trimmedName.split(" ").filter((n: string) => n.length > 0);

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

    let lines: string[] = [];
    if (trimmedLongHelp.length > 1) {
      lines = trimmedLongHelp.split("\n").filter((l: string) => l.length > 0);
    }

    const nodeUrl = `${workspaceUrl}/CommandTree/Nodes/aaz/${commandGroup.names.join("/")}`;

    try {
      const res = await updateCommandGroupOperation.execute(nodeUrl, {
        help: {
          short: trimmedShortHelp,
          lines: lines,
        },
        stage: stage,
      });

      const finalName = names.join(" ");
      if (finalName === commandGroup.names.join(" ")) {
        const cmdGroup = DecodeResponseCommandGroup(res);
        onClose(cmdGroup);
      } else {
        const renameRes = await renameCommandGroupOperation.execute(nodeUrl, finalName);
        const cmdGroup = DecodeResponseCommandGroup(renameRes);
        onClose(cmdGroup);
      }
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
    }
  }, [
    name,
    shortHelp,
    longHelp,
    stage,
    workspaceUrl,
    commandGroup.names,
    onClose,
    updateCommandGroupOperation,
    renameCommandGroupOperation,
  ]);

  const handleClose = React.useCallback(() => {
    setInvalidText(undefined);
    onClose();
  }, [onClose]);

  return (
    <Dialog disableEscapeKeyDown open={open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
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
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
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
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
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
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
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
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
            setLongHelp(event.target.value);
          }}
          margin="normal"
        />
        {<AsyncOperationBanner operation={updateCommandGroupOperation} />}
        {<AsyncOperationBanner operation={renameCommandGroupOperation} />}
      </DialogContent>
      <DialogActions>
        {!updateCommandGroupOperation.loading && !renameCommandGroupOperation.loading && (
          <React.Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleModify}>Save</Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CommandGroupDialog;
