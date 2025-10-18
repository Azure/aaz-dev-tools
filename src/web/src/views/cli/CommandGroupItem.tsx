import * as React from "react";
import TreeItem from "@mui/lab/TreeItem";
import FolderIcon from "@mui/icons-material/Folder";
import { Box, Checkbox, Typography, styled, TypographyProps } from "@mui/material";
import CommandItem from "./CommandItem";
import {
  calculateSelected,
  prepareLoadCommandsOfCommandGroup,
  type ProfileCTCommandGroup,
  type ProfileCTCommand,
} from "./utils/commandTreeUtils";

const CommandGroupTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 17,
  fontWeight: 600,
}));

interface CommandGroupItemProps {
  commandGroup: ProfileCTCommandGroup;
  onUpdateCommandGroup: (
    name: string,
    updater: (oldCommandGroup: ProfileCTCommandGroup) => ProfileCTCommandGroup,
  ) => void;
  onLoadCommands: (names: string[][]) => Promise<void>;
}

const CommandGroupItem: React.FC<CommandGroupItemProps> = React.memo(
  ({ commandGroup, onUpdateCommandGroup, onLoadCommands }) => {
    const nodeName = commandGroup.names[commandGroup.names.length - 1];
    const selected = commandGroup.selected ?? false;

    const onUpdateCommand = React.useCallback(
      (name: string, updater: (oldCommand: ProfileCTCommand) => ProfileCTCommand) => {
        onUpdateCommandGroup(nodeName, (oldCommandGroup) => {
          const commands = {
            ...oldCommandGroup.commands,
            [name]: updater(oldCommandGroup.commands![name]),
          };
          const selected = calculateSelected(commands, oldCommandGroup.commandGroups ?? {});
          return {
            ...oldCommandGroup,
            commands: commands,
            selected: selected,
          };
        });
      },
      [onUpdateCommandGroup, nodeName],
    );

    const onUpdateSubCommandGroup = React.useCallback(
      (name: string, updater: (oldCommandGroup: ProfileCTCommandGroup) => ProfileCTCommandGroup) => {
        onUpdateCommandGroup(nodeName, (oldCommandGroup) => {
          const commandGroups = {
            ...oldCommandGroup.commandGroups,
            [name]: updater(oldCommandGroup.commandGroups![name]),
          };
          const commands = oldCommandGroup.commands;
          const selected = calculateSelected(commands ?? {}, commandGroups);
          return {
            ...oldCommandGroup,
            commandGroups: commandGroups,
            selected: selected,
          };
        });
      },
      [onUpdateCommandGroup, nodeName],
    );

    const onLoadCommand = React.useCallback(
      async (names: string[]) => {
        await onLoadCommands([names]);
      },
      [onLoadCommands],
    );

    const updateCommandSelected = (command: ProfileCTCommand, selected: boolean): ProfileCTCommand => {
      if (selected === command.selected) {
        return command;
      }
      return {
        ...command,
        selected: selected,
        selectedVersion: selected
          ? command.selectedVersion
            ? command.selectedVersion
            : command.versions
              ? command.versions[0].name
              : undefined
          : command.selectedVersion,
        modified: true,
      };
    };

    const updateGroupSelected = (group: ProfileCTCommandGroup, selected: boolean): ProfileCTCommandGroup => {
      if (selected === group.selected) {
        return group;
      }
      const commands = group.commands
        ? Object.fromEntries(
            Object.entries(group.commands).map(([key, value]) => [key, updateCommandSelected(value, selected)]),
          )
        : undefined;
      const commandGroups = group.commandGroups
        ? Object.fromEntries(
            Object.entries(group.commandGroups).map(([key, value]) => [key, updateGroupSelected(value, selected)]),
          )
        : undefined;
      return {
        ...group,
        commands: commands,
        commandGroups: commandGroups,
        selected: selected,
      };
    };

    const selectCommandGroup = React.useCallback(
      (selected: boolean) => {
        onUpdateCommandGroup(nodeName, (oldCommandGroup) => {
          const selectedGroup = updateGroupSelected(oldCommandGroup, selected);
          const [loadingNamesList, newGroup] = prepareLoadCommandsOfCommandGroup(selectedGroup);
          if (loadingNamesList.length > 0) {
            onLoadCommands(loadingNamesList);
          }
          return newGroup;
        });
      },
      [onUpdateCommandGroup, onLoadCommands, nodeName],
    );

    return (
      <TreeItem
        sx={{ marginLeft: 2, marginTop: 0.5 }}
        key={commandGroup.id}
        nodeId={commandGroup.id}
        color="inherit"
        data-testid={`command-group-${commandGroup.id}`}
        label={
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "flex-start",
            }}
          >
            <Checkbox
              disableRipple
              checked={commandGroup.selected !== false}
              indeterminate={commandGroup.selected === undefined}
              onClick={(event) => {
                selectCommandGroup(!selected);
                event.stopPropagation();
                event.preventDefault();
              }}
            />
            <FolderIcon />
            <CommandGroupTypography sx={{ marginLeft: 1 }}>{nodeName}</CommandGroupTypography>
          </Box>
        }
      >
        {commandGroup.commands !== undefined &&
          Object.values(commandGroup.commands).map((command) => (
            <CommandItem
              key={command.id}
              command={command}
              onUpdateCommand={onUpdateCommand}
              onLoadCommand={onLoadCommand}
            />
          ))}
        {commandGroup.commandGroups !== undefined &&
          Object.values(commandGroup.commandGroups).map((group) => (
            <CommandGroupItem
              key={group.id}
              commandGroup={group}
              onUpdateCommandGroup={onUpdateSubCommandGroup}
              onLoadCommands={onLoadCommands}
            />
          ))}
      </TreeItem>
    );
  },
);

CommandGroupItem.displayName = "CommandGroupItem";

export default CommandGroupItem;

export type { CommandGroupItemProps };
