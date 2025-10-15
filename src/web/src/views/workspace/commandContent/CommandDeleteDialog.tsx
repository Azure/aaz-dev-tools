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
import React from "react";
import { commandApi } from "../../../services";
import { COMMAND_PREFIX } from "../../../constants";
import { Command, ResponseCommand, DecodeResponseCommand } from "./WSEditorCommandContent";

export interface CommandDeleteDialogProps {
  workspaceUrl: string;
  open: boolean;
  command: Command;
  onClose: (deleted: boolean) => void;
}

const CommandDeleteDialog: React.FC<CommandDeleteDialogProps> = (props) => {
  const [updating, setUpdating] = React.useState<boolean>(false);
  const [relatedCommands, setRelatedCommands] = React.useState<string[]>([]);

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

  React.useEffect(() => {
    setRelatedCommands([]);
    const urls = getUrls();
    const promisesAll = urls.map(async (url) => {
      return await commandApi.getCommandsForResource(url);
    });
    Promise.all(promisesAll)
      .then((responses) => {
        const commands = new Set<string>();
        responses.forEach((responseCommands: ResponseCommand[]) => {
          responseCommands
            .map((responseCommand) => DecodeResponseCommand(responseCommand))
            .forEach((cmd) => {
              commands.add(cmd.names.join(" "));
            });
        });

        const cmdNames: string[] = [];
        commands.forEach((cmdName) => cmdNames.push(cmdName));
        cmdNames.sort((a, b) => a.localeCompare(b));
        setRelatedCommands(cmdNames);
      })
      .catch((err) => {
        console.error(err);
      });
  }, [props.command]);

  const handleClose = () => {
    props.onClose(false);
  };

  const handleDelete = () => {
    setUpdating(true);
    const urls = getUrls();
    const promisesAll = urls.map(async (url) => {
      return await commandApi.deleteResource(url);
    });
    Promise.all(promisesAll)
      .then(() => {
        setUpdating(false);
        props.onClose(true);
      })
      .catch((err) => {
        setUpdating(false);
        console.error(err);
      });
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
          <React.Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleDelete}>Delete</Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CommandDeleteDialog;
