import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Typography } from "@mui/material";
import React, { useState, useEffect } from "react";
import { commandApi } from "../../../../services";
import { useAsyncOperation } from "../../../../services/hooks";
import { AsyncOperationBanner } from "../../../../components";
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
  const deleteOperation = useAsyncOperation(commandApi.deleteResource);
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
    const urls = getUrls();

    try {
      await Promise.all(urls.map((url) => deleteOperation.execute(url)));
      props.onClose(true);
    } catch (error) {
      console.error("Delete failed:", error);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      {!deleteOperation.loading && <DialogTitle>Delete Commands</DialogTitle>}
      <DialogContent dividers={true}>
        <AsyncOperationBanner operation={deleteOperation} />
        {relatedCommands.map((command, idx) => (
          <Typography key={`command-${idx}`} variant="body2">{`${COMMAND_PREFIX}${command}`}</Typography>
        ))}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={deleteOperation.loading}>
          Cancel
        </Button>
        <Button onClick={handleDelete} disabled={deleteOperation.loading}>
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CommandDeleteDialog;
