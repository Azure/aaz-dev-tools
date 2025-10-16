import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  Typography,
} from "@mui/material";
import React, { useState, useEffect } from "react";
import { commandApi } from "../../../../services";
import { COMMAND_PREFIX } from "../../../../constants";
import { DecodeResponseCommand } from "../../utils/decodeResponseCommand";
import type { Command, ResponseCommand } from "../../interfaces";

export interface CommandDeleteDialogProps {
  workspaceUrl: string;
  open: boolean;
  command: Command;
  onClose: (deleted: boolean) => void;
}

const CommandDeleteDialog: React.FC<CommandDeleteDialogProps> = (props) => {
  const [updating, setUpdating] = useState<boolean>(false);
  const [relatedCommands, setRelatedCommands] = useState<string[]>([]);

  const getUrls = () => {
    const urls: string[] = [];

    props.command.resources.forEach((resource) => {
      const resourceId = btoa(resource.id);
      const version = btoa(resource.version);
      if (resource.subresource !== undefined) {
        const subresource = btoa(resource.subresource);
        urls.push(`${props.workspaceUrl}/Resources/${resourceId}/V/${version}/Subresources/${subresource}`);
      } else {
        urls.push(`${props.workspaceUrl}/Resources/${resourceId}/V/${version}`);
      }
    });
    return urls;
  };

  useEffect(() => {
    const fetchRelatedCommands = async () => {
      setRelatedCommands([]);
      const urls = getUrls();

      try {
        const responses = await Promise.all(urls.map((url) => commandApi.getCommandsForResource(url)));

        const commands = new Set<string>();
        responses.forEach((responseCommands: ResponseCommand[]) => {
          responseCommands
            .map((responseCommand) => DecodeResponseCommand(responseCommand))
            .forEach((cmd) => {
              commands.add(cmd.names.join(" "));
            });
        });

        const cmdNames = Array.from(commands).sort((a, b) => a.localeCompare(b));
        setRelatedCommands(cmdNames);
      } catch (err) {
        console.error(err);
      }
    };

    fetchRelatedCommands();
  }, [props.command]);

  const handleClose = () => {
    props.onClose(false);
  };

  const handleDelete = async () => {
    setUpdating(true);
    const urls = getUrls();

    try {
      await Promise.all(urls.map((url) => commandApi.deleteResource(url)));
      setUpdating(false);
      props.onClose(true);
    } catch (err) {
      setUpdating(false);
      console.error(err);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>Delete Commands</DialogTitle>
      <DialogContent dividers={true}>
        {relatedCommands.map((command, idx) => (
          <Typography key={`command-${idx}`} variant="body2">{`${COMMAND_PREFIX}${command}`}</Typography>
        ))}
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
            <Button onClick={handleDelete}>Delete</Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CommandDeleteDialog;
