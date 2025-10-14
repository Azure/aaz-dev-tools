import { Box, Button, Card, CardActions, CardContent, Typography } from "@mui/material";
import * as React from "react";
import { ResponseCommands } from "./WSEditorCommandContent";
import CommandGroupDialog from "./CommandGroupDialog";
import CommandGroupDeleteDialog from "./CommandGroupDeleteDialog";
import { COMMAND_PREFIX } from "../../constants";
import {
  NameTypography,
  ShortHelpTypography,
  ShortHelpPlaceHolderTypography,
  LongHelpTypography,
  StableTypography,
  PreviewTypography,
  ExperimentalTypography,
} from "./WSEditorTheme";

interface CommandGroup {
  id: string;
  names: string[];
  stage: "Stable" | "Preview" | "Experimental";
  help?: {
    short: string;
    lines?: string[];
  };
  canDelete: boolean;
}

interface ResponseCommandGroup {
  names: string[];
  stage?: "Stable" | "Preview" | "Experimental";
  help?: {
    short: string;
    lines?: string[];
  };
  commands?: ResponseCommands;
  commandGroups?: ResponseCommandGroups;
}

interface ResponseCommandGroups {
  [name: string]: ResponseCommandGroup;
}

interface WSEditorCommandGroupContentProps {
  workspaceUrl: string;
  commandGroup: CommandGroup;
  reloadTimestamp: number;
  onUpdateCommandGroup: (commandGroup: CommandGroup | null) => void;
}

const WSEditorCommandGroupContent: React.FC<WSEditorCommandGroupContentProps> = ({
  workspaceUrl,
  commandGroup,
  onUpdateCommandGroup,
}) => {
  const [displayCommandGroupDialog, setDisplayCommandGroupDialog] = React.useState<boolean>(false);
  const [displayCommandGroupDeleteDialog, setDisplayCommandGroupDeleteDialog] = React.useState<boolean>(false);

  const onCommandGroupDialogDisplay = React.useCallback(() => {
    setDisplayCommandGroupDialog(true);
  }, []);

  const onCommandGroupDeleteDialogDisplay = React.useCallback(() => {
    setDisplayCommandGroupDeleteDialog(true);
  }, []);

  const handleCommandGroupDialogClose = React.useCallback(
    (newCommandGroup?: CommandGroup) => {
      setDisplayCommandGroupDialog(false);
      if (newCommandGroup) {
        onUpdateCommandGroup(newCommandGroup);
      }
    },
    [onUpdateCommandGroup],
  );

  const handleCommandGroupDeleteDialogClose = React.useCallback(
    (deleted: boolean) => {
      setDisplayCommandGroupDeleteDialog(false);
      if (deleted) {
        onUpdateCommandGroup(null);
      }
    },
    [onUpdateCommandGroup],
  );

  const name = COMMAND_PREFIX + commandGroup.names.join(" ");
  const shortHelp = commandGroup.help?.short;
  const longHelp = commandGroup.help?.lines?.join("\n");
  const lines: string[] = commandGroup.help?.lines ?? [];
  const stage = commandGroup.stage;

  return (
    <React.Fragment>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
        }}
      >
        <Card
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
              <Typography variant="h6" sx={{ flexShrink: 0 }}>
                [ GROUP ]
              </Typography>
              <Box sx={{ flexGrow: 1 }} />
              {stage === "Stable" && <StableTypography sx={{ flexShrink: 0 }}>{stage}</StableTypography>}
              {stage === "Preview" && <PreviewTypography sx={{ flexShrink: 0 }}>{stage}</PreviewTypography>}
              {stage === "Experimental" && (
                <ExperimentalTypography sx={{ flexShrink: 0 }}>{stage}</ExperimentalTypography>
              )}
            </Box>

            <NameTypography sx={{ mt: 1 }}>{name}</NameTypography>
            {shortHelp && <ShortHelpTypography sx={{ ml: 6, mt: 2 }}> {shortHelp} </ShortHelpTypography>}
            {!shortHelp && (
              <ShortHelpPlaceHolderTypography sx={{ ml: 6, mt: 2 }}>
                Please add command group short summary!
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
                onClick={onCommandGroupDialogDisplay}
              >
                <Typography variant="body2">Edit</Typography>
              </Button>
              <Button
                variant="outlined"
                size="small"
                color="secondary"
                onClick={onCommandGroupDeleteDialogDisplay}
                disabled={!commandGroup.canDelete}
                sx={{ ml: 2 }}
              >
                <Typography variant="body2">Delete</Typography>
              </Button>
            </Box>
          </CardActions>
        </Card>
      </Box>
      {displayCommandGroupDialog && (
        <CommandGroupDialog
          open={displayCommandGroupDialog}
          workspaceUrl={workspaceUrl}
          commandGroup={commandGroup}
          onClose={handleCommandGroupDialogClose}
        />
      )}
      {displayCommandGroupDeleteDialog && (
        <CommandGroupDeleteDialog
          open={displayCommandGroupDeleteDialog}
          workspaceUrl={workspaceUrl}
          commandGroup={commandGroup}
          onClose={handleCommandGroupDeleteDialogClose}
        />
      )}
    </React.Fragment>
  );
};

const DecodeResponseCommandGroup = (commandGroup: ResponseCommandGroup): CommandGroup => {
  return {
    id: "group:" + commandGroup.names.join("/"),
    names: commandGroup.names,
    help: commandGroup.help,
    stage: commandGroup.stage ?? "Stable",
    canDelete: true,
  };
};

export default WSEditorCommandGroupContent;

export { DecodeResponseCommandGroup };
export type { CommandGroup, ResponseCommandGroup, ResponseCommandGroups };
