import React, { useCallback } from "react";
import TreeView from "@mui/lab/TreeView";
import TreeItem from "@mui/lab/TreeItem";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { Checkbox, FormControlLabel } from "@mui/material";

interface ArgSimilarArg {
  id: string;
  var: string;
  display: string;
  indexes: string[];
  isSelected: boolean;
}

interface ArgSimilarCommand {
  id: string;
  name: string;
  args: ArgSimilarArg[];
  total: number;
  selectedCount: number;
}

interface ArgSimilarGroup {
  id: string;
  name: string;
  groups?: ArgSimilarGroup[];
  commands?: ArgSimilarCommand[];
  total: number;
  selectedCount: number;
}

interface ArgSimilarTree {
  root: ArgSimilarGroup;
  selectedArgIds: string[];
}

interface ResponseArgSimilarCommand {
  id: string;
  args: {
    [argVar: string]: string[];
  };
}

interface ResponseArgSimilarGroup {
  id: string;
  commandGroups?: {
    [name: string]: ResponseArgSimilarGroup;
  };
  commands?: {
    [name: string]: ResponseArgSimilarCommand;
  };
}

const decodeResponseArgSimilarCommand = (
  responseCommand: ResponseArgSimilarCommand,
  commandName: string,
): ArgSimilarCommand => {
  const command: ArgSimilarCommand = {
    id: responseCommand.id,
    name: commandName,
    args: [],
    total: 0,
    selectedCount: 0,
  };

  Object.entries(responseCommand.args).forEach(([argVar, indexes]) => {
    const arg: ArgSimilarArg = {
      id: `${command.id}/Arguments/${argVar}`,
      var: argVar,
      indexes,
      display: "",
      isSelected: false,
    };

    if (arg.indexes.length > 1) {
      arg.display = `[${arg.var}] ${arg.indexes
        .map((idx) => {
          if (idx[1] === "." || idx[1] === "[" || idx[1] === "{") {
            return `-${idx}`;
          } else {
            return `--${idx}`;
          }
        })
        .join(" ")}`;
    } else if (arg.indexes.length === 1) {
      const idx = arg.indexes[0];
      if (idx[1] === "." || idx[1] === "[" || idx[1] === "{") {
        arg.display = `-${idx}`;
      } else {
        arg.display = `--${idx}`;
      }
    }
    command.args.push(arg);
  });

  command.total = command.args.length;
  return command;
};

const decodeResponseArgSimilarGroup = (responseGroup: ResponseArgSimilarGroup, groupName: string): ArgSimilarGroup => {
  let group: ArgSimilarGroup = {
    id: responseGroup.id,
    name: groupName,
    total: 0,
    selectedCount: 0,
  };

  if (responseGroup.commandGroups && typeof responseGroup.commandGroups === "object") {
    group.groups = Object.entries(responseGroup.commandGroups).map(([name, subGroup]) => {
      const decodedSubGroup = decodeResponseArgSimilarGroup(subGroup, name);
      group.total += decodedSubGroup.total;
      return decodedSubGroup;
    });
  }

  if (responseGroup.commands && typeof responseGroup.commands === "object") {
    group.commands = Object.entries(responseGroup.commands).map(([name, command]) => {
      const decodedCommand = decodeResponseArgSimilarCommand(command, name);
      group.total += decodedCommand.total;
      return decodedCommand;
    });
  }

  if (!group.commands && group.groups?.length === 1) {
    group = group.groups[0];
    group.name = `${groupName} ${group.name}`;
  }

  return group;
};

const gatherNodeIds = (group: ArgSimilarGroup): string[] => {
  const nodeIds: string[] = [group.id];

  group.commands?.forEach((command) => {
    nodeIds.push(command.id);
  });

  group.groups?.forEach((subGroup) => {
    nodeIds.push(...gatherNodeIds(subGroup));
  });

  return nodeIds;
};

const BuildArgSimilarTree = (response: any): { tree: ArgSimilarTree; expandedIds: string[] } => {
  const tree = {
    root: decodeResponseArgSimilarGroup(response.data.aaz, "az"),
    selectedArgIds: [],
  };
  const expandedIds = gatherNodeIds(tree.root);
  const newTree = updateSelectionStateForArgSimilarTree(tree, new Set<string>([tree.root.id]));
  return {
    tree: newTree,
    expandedIds,
  };
};

interface WSECArgumentSimilarPickerProps {
  tree: ArgSimilarTree;
  expandedIds: string[];
  updatedIds: string[];
  onTreeUpdated: (tree: ArgSimilarTree) => void;
  onToggle: (nodeIds: string[]) => void;
}

const updateSelectionStateForArgSimilarCommand = (
  command: ArgSimilarCommand,
  selectedIds: Set<string>,
): { command: ArgSimilarCommand; selectedArgIds: string[] } => {
  const newSelectedIds: string[] = [];
  const newCommand = {
    ...command,
    args: command.args.map((arg) => {
      let isSelected = selectedIds.has(arg.id);
      if (!isSelected) {
        const idParts = arg.id.split("/");
        for (let idx = 1; idx < idParts.length; idx += 1) {
          const newId = idParts.slice(0, idx + 1).join("/");
          if (selectedIds.has(newId)) {
            isSelected = true;
            break;
          }
        }
      }
      if (isSelected) {
        newSelectedIds.push(arg.id);
      }

      return {
        ...arg,
        indexes: [...arg.indexes],
        isSelected,
      };
    }),
  };

  newCommand.selectedCount = newSelectedIds.length;

  return {
    command: newCommand,
    selectedArgIds: newSelectedIds,
  };
};

const updateSelectionStateForArgSimilarGroup = (
  group: ArgSimilarGroup,
  selectedIds: Set<string>,
): { group: ArgSimilarGroup; selectedArgIds: string[] } => {
  let newSelectedIds: string[] = [];
  const newGroup = {
    ...group,
    groups: group.groups?.map((subGroup) => {
      const { group: newSubGroup, selectedArgIds: subSelectedIds } = updateSelectionStateForArgSimilarGroup(
        subGroup,
        selectedIds,
      );
      newSelectedIds.push(...subSelectedIds);
      return newSubGroup;
    }),
    commands: group.commands?.map((command) => {
      const { command: newCommand, selectedArgIds: subSelectedIds } = updateSelectionStateForArgSimilarCommand(
        command,
        selectedIds,
      );
      newSelectedIds.push(...subSelectedIds);
      return newCommand;
    }),
  };

  newGroup.selectedCount = newSelectedIds.length;

  return {
    group: newGroup,
    selectedArgIds: newSelectedIds,
  };
};

const updateSelectionStateForArgSimilarTree = (tree: ArgSimilarTree, selectedIds: Set<string>): ArgSimilarTree => {
  const { group, selectedArgIds } = updateSelectionStateForArgSimilarGroup(tree.root, selectedIds);
  return {
    root: group,
    selectedArgIds,
  };
};

const WSECArgumentSimilarPicker: React.FC<WSECArgumentSimilarPickerProps> = ({
  tree,
  expandedIds,
  updatedIds,
  onTreeUpdated,
  onToggle,
}) => {
  const onCheckItem = useCallback(
    (itemId: string, select: boolean) => {
      let selectedIds: Set<string>;
      if (select) {
        selectedIds = new Set(tree.selectedArgIds).add(itemId);
      } else {
        selectedIds = new Set(tree.selectedArgIds.filter((id) => id !== itemId && !id.startsWith(`${itemId}/`)));
      }
      onTreeUpdated(updateSelectionStateForArgSimilarTree(tree, selectedIds));
    },
    [tree, onTreeUpdated],
  );

  const onNodeToggle = useCallback(
    (event: React.SyntheticEvent, nodeIds: string[]) => {
      onToggle(nodeIds);
      event.stopPropagation();
      event.preventDefault();
    },
    [onToggle],
  );

  const renderArg = useCallback(
    (arg: ArgSimilarArg) => {
      const isUpdated = updatedIds.includes(arg.id);
      return (
        <TreeItem
          key={arg.id}
          nodeId={arg.id}
          color="inherit"
          label={
            <FormControlLabel
              control={
                <Checkbox
                  size="small"
                  checked={arg.isSelected}
                  onClick={(event) => {
                    onCheckItem(arg.id, !arg.isSelected);
                    event.stopPropagation();
                    event.preventDefault();
                  }}
                  disabled={isUpdated}
                />
              }
              label={arg.display}
              sx={{
                paddingLeft: 1,
              }}
            />
          }
        />
      );
    },
    [updatedIds, onCheckItem],
  );

  const renderCommand = useCallback(
    (command: ArgSimilarCommand) => {
      return (
        <TreeItem
          key={command.id}
          nodeId={command.id}
          color="inherit"
          label={
            <FormControlLabel
              control={
                <Checkbox
                  size="small"
                  checked={command.selectedCount > 0 && command.selectedCount === command.total}
                  indeterminate={command.selectedCount > 0 && command.selectedCount < command.total}
                  onClick={(event) => {
                    onCheckItem(command.id, !(command.selectedCount > 0 && command.selectedCount === command.total));
                    event.stopPropagation();
                    event.preventDefault();
                  }}
                />
              }
              label={command.name}
              sx={{
                paddingLeft: 1,
              }}
            />
          }
        >
          {command.args?.map((arg) => renderArg(arg))}
        </TreeItem>
      );
    },
    [onCheckItem, renderArg],
  );

  const renderGroup = useCallback(
    (group: ArgSimilarGroup): React.ReactElement => {
      return (
        <TreeItem
          key={group.id}
          nodeId={group.id}
          color="inherit"
          label={
            <FormControlLabel
              control={
                <Checkbox
                  size="small"
                  checked={group.selectedCount > 0 && group.selectedCount === group.total}
                  indeterminate={group.selectedCount > 0 && group.selectedCount < group.total}
                  onClick={(event) => {
                    onCheckItem(group.id, !(group.selectedCount > 0 && group.selectedCount === group.total));
                    event.stopPropagation();
                    event.preventDefault();
                  }}
                />
              }
              label={group.name}
              sx={{
                paddingLeft: 1,
              }}
            />
          }
        >
          {group.commands?.map((command) => renderCommand(command))}
          {group.groups?.map((subGroup) => renderGroup(subGroup))}
        </TreeItem>
      );
    },
    [onCheckItem, renderCommand],
  );

  return (
    <TreeView
      sx={{
        flexGrow: 1,
        overflowY: "auto",
      }}
      defaultCollapseIcon={<ExpandMoreIcon />}
      defaultExpandIcon={<ChevronRightIcon />}
      onNodeToggle={onNodeToggle}
      selected={[]}
      expanded={expandedIds}
    >
      {renderGroup(tree.root)}
    </TreeView>
  );
};

export default WSECArgumentSimilarPicker;
export { BuildArgSimilarTree };
export type { ArgSimilarTree, ArgSimilarGroup, ArgSimilarCommand, ArgSimilarArg };
