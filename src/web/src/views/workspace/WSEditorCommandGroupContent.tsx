import { Box, Button, Card, CardActions, CardContent, Typography } from "@mui/material";
import * as React from "react";
import { ResponseCommands } from "./WSEditorCommandContent";
import CommandGroupDialog from "./CommandGroupDialog";
import CommandGroupDeleteDialog from "./CommandGroupDeleteDialog";
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

const commandPrefix = "az ";

interface WSEditorCommandGroupContentProps {
  workspaceUrl: string;
  commandGroup: CommandGroup;
  reloadTimestamp: number;
  onUpdateCommandGroup: (commandGroup: CommandGroup | null) => void;
}

interface WSEditorCommandGroupContentState {
  displayCommandGroupDialog: boolean;
  displayCommandGroupDeleteDialog: boolean;
}

class WSEditorCommandGroupContent extends React.Component<
  WSEditorCommandGroupContentProps,
  WSEditorCommandGroupContentState
> {
  constructor(props: WSEditorCommandGroupContentProps) {
    super(props);
    this.state = {
      displayCommandGroupDialog: false,
      displayCommandGroupDeleteDialog: false,
    };
  }

  onCommandGroupDialogDisplay = () => {
    this.setState({
      displayCommandGroupDialog: true,
    });
  };

  onCommandGroupDeleteDialogDisplay = () => {
    this.setState({
      displayCommandGroupDeleteDialog: true,
    });
  };

  handleCommandGroupDialogClose = (newCommandGroup?: CommandGroup) => {
    this.setState({
      displayCommandGroupDialog: false,
    });
    if (newCommandGroup) {
      this.props.onUpdateCommandGroup(newCommandGroup!);
    }
  };

  handleCommandGroupDeleteDialogClose = (deleted: boolean) => {
    this.setState({
      displayCommandGroupDeleteDialog: false,
    });
    if (deleted) {
      this.props.onUpdateCommandGroup(null);
    }
  };

  render() {
    const { workspaceUrl, commandGroup } = this.props;
    const name = commandPrefix + this.props.commandGroup.names.join(" ");
    const shortHelp = this.props.commandGroup.help?.short;
    const longHelp = this.props.commandGroup.help?.lines?.join("\n");
    const lines: string[] = this.props.commandGroup.help?.lines ?? [];
    const stage = this.props.commandGroup.stage;
    const { displayCommandGroupDialog, displayCommandGroupDeleteDialog } = this.state;
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
            // variant='outlined'
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
                  onClick={this.onCommandGroupDialogDisplay}
                >
                  <Typography variant="body2">Edit</Typography>
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  color="secondary"
                  onClick={this.onCommandGroupDeleteDialogDisplay}
                  disabled={!this.props.commandGroup.canDelete}
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
            onClose={this.handleCommandGroupDialogClose}
          />
        )}
        {displayCommandGroupDeleteDialog && (
          <CommandGroupDeleteDialog
            open={displayCommandGroupDeleteDialog}
            workspaceUrl={workspaceUrl}
            commandGroup={commandGroup}
            onClose={this.handleCommandGroupDeleteDialogClose}
          />
        )}
      </React.Fragment>
    );
  }
}

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
