import React, { memo, useCallback } from "react";
import TreeItem from "@mui/lab/TreeItem";
import EditIcon from "@mui/icons-material/Edit";
import {
  Box,
  Checkbox,
  FormControl,
  Typography,
  Select,
  MenuItem,
  styled,
  TypographyProps,
  InputLabel,
  IconButton,
} from "@mui/material";
import { type ProfileCTCommand } from "./utils/commandTreeUtils";

const CommandTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.primary.main,
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 20,
  fontWeight: 400,
}));

const SelectionTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
  color: theme.palette.grey[700],
  fontFamily: "'Work Sans', sans-serif",
  fontSize: 15,
  fontWeight: 400,
}));

const RegisteredTypography = styled(SelectionTypography)<TypographyProps>(() => ({}));

const UnregisteredTypography = styled(SelectionTypography)<TypographyProps>(() => ({
  color: "#d9c136",
}));

interface CommandItemProps {
  command: ProfileCTCommand;
  onUpdateCommand: (name: string, updater: (oldCommand: ProfileCTCommand) => ProfileCTCommand) => void;
  onLoadCommand(names: string[]): Promise<void>;
}

const CommandItem: React.FC<CommandItemProps> = memo(({ command, onUpdateCommand, onLoadCommand }) => {
  const leafName = command.names[command.names.length - 1];

  const selectCommand = useCallback(
    (selected: boolean) => {
      onUpdateCommand(leafName, (oldCommand) => {
        if (oldCommand.versions === undefined && selected === true) {
          onLoadCommand(oldCommand.names);
        }
        return {
          ...oldCommand,
          loading: selected && oldCommand.versions === undefined,
          selected: selected,
          selectedVersion: selected
            ? oldCommand.selectedVersion
              ? oldCommand.selectedVersion
              : oldCommand.versions
                ? oldCommand.versions[0].name
                : undefined
            : oldCommand.selectedVersion,
          modified: true,
        };
      });
    },
    [onUpdateCommand, onLoadCommand, leafName],
  );

  const selectVersion = useCallback(
    (version: string) => {
      onUpdateCommand(leafName, (oldCommand) => {
        return {
          ...oldCommand,
          selectedVersion: version,
          modified: true,
        };
      });
    },
    [onUpdateCommand, leafName],
  );

  const selectRegistered = useCallback(
    (registered: boolean) => {
      onUpdateCommand(leafName, (oldCommand) => {
        return {
          ...oldCommand,
          registered: registered,
          modified: true,
        };
      });
    },
    [onUpdateCommand, leafName],
  );

  return (
    <TreeItem
      sx={{ marginLeft: 2 }}
      key={command.id}
      nodeId={command.id}
      color="inherit"
      label={
        <Box
          sx={{
            marginTop: 1,
            marginBottom: 1,
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "flex-start",
          }}
        >
          <Checkbox
            disableRipple
            checked={command.selected}
            onClick={(event) => {
              selectCommand(!command.selected);
              event.stopPropagation();
              event.preventDefault();
            }}
          />
          <Box
            sx={{
              marginLeft: 1,
              minWidth: 100,
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "flex-start",
            }}
          >
            <CommandTypography>{leafName}</CommandTypography>
            <Box
              sx={{
                marginLeft: 1,
                width: 20,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {!command.modified && command.selectedVersion !== undefined && (
                <IconButton
                  onClick={(_event) => {
                    selectCommand(true);
                  }}
                >
                  <EditIcon fontSize="small" color="disabled" />
                </IconButton>
              )}
              {command.modified && <EditIcon fontSize="small" color="secondary" />}
            </Box>
          </Box>
          {command.versions !== undefined && command.selectedVersion !== undefined && (
            <Box
              sx={{
                marginLeft: 1,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "flex-start",
              }}
            >
              <FormControl
                sx={{
                  minWidth: 150,
                  marginLeft: 1,
                }}
                size="small"
                variant="standard"
              >
                <InputLabel>Version</InputLabel>
                <Select
                  id={`${command.id}-version-select`}
                  value={command.selectedVersion}
                  onChange={(event) => {
                    selectVersion(event.target.value);
                  }}
                  size="small"
                >
                  {command.versions!.map((version) => (
                    <MenuItem value={version.name} key={`${command.id}-version-select-${version.name}`}>
                      <SelectionTypography>{version.name}</SelectionTypography>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl
                sx={{
                  minWidth: 150,
                  marginLeft: 1,
                }}
                size="small"
                variant="standard"
              >
                <InputLabel>Command table</InputLabel>
                <Select
                  id={`${command.id}-register-select`}
                  value={command.registered ? 1 : 0}
                  onChange={(event) => {
                    selectRegistered(event.target.value === 1);
                  }}
                  size="small"
                >
                  <MenuItem value={1} key={`${command.id}-register-select-registered`}>
                    <RegisteredTypography>Registered</RegisteredTypography>
                  </MenuItem>
                  <MenuItem value={0} key={`${command.id}-register-select-unregistered`}>
                    <UnregisteredTypography>Unregistered</UnregisteredTypography>
                  </MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
          {command.loading === true && command.selected && (
            <Box
              sx={{
                marginLeft: 1,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "flex-start",
              }}
            >
              <Typography variant="body2" color="textSecondary">
                Loading...
              </Typography>
            </Box>
          )}
        </Box>
      }
      onClick={(event) => {
        event.stopPropagation();
        event.preventDefault();
      }}
    />
  );
});

CommandItem.displayName = "CommandItem";

export default CommandItem;

export type { CommandItemProps };
