import React, { useState, useCallback, useEffect } from "react";
import TreeView from "@mui/lab/TreeView";

import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { CLISpecsCommand } from "./CLIModuleGenerator";
import CommandGroupItem from "./CommandGroupItem";
import {
  calculateSelected,
  prepareLoadCommandsOfCommandGroup,
  type ProfileCTCommandGroup,
  type ProfileCTCommand,
} from "./utils/commandTreeUtils";
import {
  ProfileCommandTree,
  initializeCommandTreeByModView,
  exportModViewProfile,
  decodeProfileCTCommand,
} from "./utils/commandTreeInitialization";

interface CLIModGeneratorProfileCommandTreeProps {
  profile?: string;
  profileCommandTree: ProfileCommandTree;
  onChange: (updater: ((oldProfileCommandTree: ProfileCommandTree) => ProfileCommandTree) | ProfileCommandTree) => void;
  onLoadCommands: (namesList: string[][]) => Promise<CLISpecsCommand[]>;
}

const CLIModGeneratorProfileCommandTree: React.FC<CLIModGeneratorProfileCommandTreeProps> = ({
  profileCommandTree,
  onChange,
  onLoadCommands,
}) => {
  const [defaultExpanded, _] = useState(getDefaultExpanded(profileCommandTree));

  const onUpdateCommandGroup = useCallback(
    (name: string, updater: (oldCommandGroup: ProfileCTCommandGroup) => ProfileCTCommandGroup) => {
      onChange((profileCommandTree) => {
        return {
          ...profileCommandTree,
          commandGroups: {
            ...profileCommandTree.commandGroups,
            [name]: updater(profileCommandTree.commandGroups[name]),
          },
        };
      });
    },
    [onChange],
  );

  const handleBatchedLoadedCommands = useCallback(
    (commands: CLISpecsCommand[]) => {
      onChange((profileCommandTree) => {
        const newTree = commands.reduce((tree, command) => {
          return (
            genericUpdateCommand(tree, command.names, (unloadedCommand) => {
              return decodeProfileCTCommand(
                command,
                unloadedCommand.selected,
                unloadedCommand.modified,
                unloadedCommand.registered,
                unloadedCommand.selectedVersion,
              );
            }) ?? tree
          );
        }, profileCommandTree);
        return newTree;
      });
    },
    [onChange],
  );

  const onLoadAndDecodeCommands = useCallback(
    async (names: string[][]) => {
      const commands = await onLoadCommands(names);
      handleBatchedLoadedCommands(commands);
    },
    [onLoadCommands],
  );

  useEffect(() => {
    const [loadingNamesList, newTree] = prepareLoadCommands(profileCommandTree);
    if (loadingNamesList.length > 0) {
      onChange(newTree);
      onLoadCommands(loadingNamesList).then((commands) => {
        handleBatchedLoadedCommands(commands);
      });
    }
  }, [profileCommandTree]);

  return (
    <React.Fragment>
      <TreeView
        disableSelection={true}
        defaultExpanded={defaultExpanded}
        defaultCollapseIcon={<ArrowDropDownIcon />}
        defaultExpandIcon={<ArrowRightIcon />}
        data-testid="cli-command-tree"
      >
        {Object.values(profileCommandTree.commandGroups).map((commandGroup) => (
          <CommandGroupItem
            key={commandGroup.id}
            commandGroup={commandGroup}
            onUpdateCommandGroup={onUpdateCommandGroup}
            onLoadCommands={onLoadAndDecodeCommands}
          />
        ))}
      </TreeView>
    </React.Fragment>
  );
};

const getDefaultExpandedOfCommandGroup = (commandGroup: ProfileCTCommandGroup): string[] => {
  const expandedIds = commandGroup.commandGroups
    ? Object.values(commandGroup.commandGroups).flatMap((value) =>
        value.selected !== false ? [value.id, ...getDefaultExpandedOfCommandGroup(value)] : [],
      )
    : [];
  return expandedIds;
};

const getDefaultExpanded = (tree: ProfileCommandTree): string[] => {
  return Object.values(tree.commandGroups).flatMap((value) => {
    const ids = getDefaultExpandedOfCommandGroup(value);
    if (value.selected !== false) {
      ids.push(value.id);
    }
    return ids;
  });
};

const prepareLoadCommands = (tree: ProfileCommandTree): [string[][], ProfileCommandTree] => {
  const namesList: string[][] = [];
  const commandGroups = Object.fromEntries(
    Object.entries(tree.commandGroups).map(([key, value]) => {
      const [namesListSub, updatedGroup] = prepareLoadCommandsOfCommandGroup(value);
      namesList.push(...namesListSub);
      return [key, updatedGroup];
    }),
  );
  if (namesList.length > 0) {
    return [
      namesList,
      {
        ...tree,
        commandGroups: commandGroups,
      },
    ];
  } else {
    return [[], tree];
  }
};

const genericUpdateCommand = (
  tree: ProfileCommandTree,
  names: string[],
  updater: (command: ProfileCTCommand) => ProfileCTCommand | undefined,
): ProfileCommandTree | undefined => {
  const nodes: ProfileCTCommandGroup[] = [];
  for (const name of names.slice(0, -1)) {
    const node = nodes.length === 0 ? tree : nodes[nodes.length - 1];
    if (node.commandGroups === undefined) {
      throw new Error("Invalid names: " + names.join(" "));
    }
    nodes.push(node.commandGroups[name]);
  }
  let currentCommandGroup = nodes[nodes.length - 1];
  const updatedCommand = updater(currentCommandGroup.commands![names[names.length - 1]]);
  if (updatedCommand === undefined) {
    return undefined;
  }
  const commands = {
    ...currentCommandGroup.commands,
    [names[names.length - 1]]: updatedCommand,
  };
  const groupSelected = calculateSelected(commands, currentCommandGroup.commandGroups!);
  currentCommandGroup = {
    ...currentCommandGroup,
    commands: commands,
    selected: groupSelected,
  };
  for (const node of nodes.reverse().slice(1)) {
    const commandGroups = {
      ...node.commandGroups,
      [currentCommandGroup.names[currentCommandGroup.names.length - 1]]: currentCommandGroup,
    };
    const selected = calculateSelected(node.commands ?? {}, commandGroups);
    currentCommandGroup = {
      ...node,
      commandGroups: commandGroups,
      selected: selected,
    };
  }
  return {
    ...tree,
    commandGroups: {
      ...tree.commandGroups,
      [currentCommandGroup.names[currentCommandGroup.names.length - 1]]: currentCommandGroup,
    },
  };
};

export default CLIModGeneratorProfileCommandTree;

export type { ProfileCommandTree };

export { initializeCommandTreeByModView, exportModViewProfile };
