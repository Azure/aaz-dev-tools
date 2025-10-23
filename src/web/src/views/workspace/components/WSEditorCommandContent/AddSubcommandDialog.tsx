import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormLabel,
  LinearProgress,
  TextField,
} from "@mui/material";
import React, { useState, useEffect } from "react";
import { commandApi, errorHandlerApi } from "../../../../services";
import type { Command } from "../../interfaces";

export interface AddSubcommandDialogProps {
  workspaceUrl: string;
  command: Command;
  argVar: string;
  subArgOptions: { var: string; options: string }[];
  defaultGroupNames: string[];
  open: boolean;
  onClose: (added: boolean) => void;
}

const AddSubcommandDialog: React.FC<AddSubcommandDialogProps> = ({
  workspaceUrl,
  command,
  argVar,
  subArgOptions,
  defaultGroupNames,
  open,
  onClose,
}) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [commandGroupName, setCommandGroupName] = useState<string>("");
  const [refArgsOptions, setRefArgsOptions] = useState<{ var: string; options: string }[]>([]);

  useEffect(() => {
    setCommandGroupName(defaultGroupNames.join(" "));
    setRefArgsOptions(subArgOptions);
  }, [argVar, defaultGroupNames, subArgOptions]);

  const handleClose = () => {
    setInvalidText(undefined);
    onClose(false);
  };

  const verifyAddSubresource = () => {
    setInvalidText(undefined);
    const argOptions: { [argVar: string]: string[] } = {};
    let invalidText: string | undefined = undefined;
    refArgsOptions.forEach((arg, idx) => {
      const names = arg.options.split(" ").filter((n) => n.length > 0);
      if (names.length < 1) {
        invalidText = `Prop ${idx + 1} option name is required.`;
        return undefined;
      }

      for (const idx in names) {
        const piece = names[idx];
        if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(piece)) {
          invalidText = `Invalid 'Prop ${idx + 1} option name': '${piece}'. Supported regular expression is: [a-z0-9]+(-[a-z0-9]+)* `;
          return undefined;
        }
      }
      argOptions[arg.var] = names;
    });

    const names = commandGroupName.split(" ").filter((n) => n.length > 0);
    if (names.length < 1) {
      invalidText = "Invalid Command group name";
      return;
    }

    if (invalidText !== undefined) {
      setInvalidText(invalidText);
      return undefined;
    }

    return {
      commandGroupName: names.join(" "),
      refArgsOptions: argOptions,
    };
  };

  const handleAddSubresource = async () => {
    const urls = command.resources.map((resource) => {
      const resourceId = btoa(resource.id);
      const version = btoa(resource.version);
      return `${workspaceUrl}/Resources/${resourceId}/V/${version}/Subresources`;
    });

    if (urls.length !== 1) {
      setInvalidText(`Cannot create subcommands, command contains ${command.resources.length} resources`);
      return;
    }

    const data = verifyAddSubresource();
    if (data === undefined) {
      return;
    }

    setUpdating(true);

    try {
      await commandApi.createSubresource(urls[0], {
        ...data,
        arg: argVar,
      });
      onClose(true);
    } catch (err: any) {
      console.error(err);
      const message = errorHandlerApi.getErrorMessage(err);
      setInvalidText(`ResponseError: ${message}`);
      setUpdating(false);
    }
  };

  const buildRefArgText = (arg: { var: string; options: string }, idx: number) => {
    return (
      <TextField
        id={`subArg-${arg.var}`}
        key={arg.var}
        label={`${arg.var}`}
        helperText={idx === 0 ? "You can input multiple names separated by a space character" : undefined}
        type="text"
        fullWidth
        variant="standard"
        value={arg.options}
        onChange={(event: any) => {
          const options = refArgsOptions.map((value) => {
            if (value.var === arg.var) {
              return {
                ...value,
                options: event.target.value,
              };
            } else {
              return value;
            }
          });
          setRefArgsOptions(options);
        }}
        margin="normal"
        required
      />
    );
  };

  return (
    <Dialog disableEscapeKeyDown open={open} sx={{ "& .MuiDialog-paper": { width: "80%" } }}>
      <DialogTitle>Add Subcommands</DialogTitle>
      <DialogContent dividers={true}>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        <FormLabel>Subcommand Group</FormLabel>
        <TextField
          id="subcommand-group-name"
          label="name"
          placeholder="Please input command group name for subcommands"
          type="text"
          variant="standard"
          value={commandGroupName}
          fullWidth
          margin="normal"
          required
          onChange={(event: any) => {
            setCommandGroupName(event.target.value);
          }}
        />
        {refArgsOptions.length > 0 && (
          <>
            <FormLabel>Argument Options</FormLabel>
            {refArgsOptions.map(buildRefArgText)}
          </>
        )}
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
          <>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleAddSubresource}>Add Subcommands</Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default AddSubcommandDialog;
