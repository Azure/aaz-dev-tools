import React, { useState, useCallback, useEffect } from "react";
import TreeView from "@mui/lab/TreeView";

import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import {
  CLIModViewCommand,
  CLIModViewCommandGroup,
  CLIModViewCommandGroups,
  CLIModViewCommands,
  CLIModViewProfile,
} from "./interfaces";
import {
  CLISpecsCommand,
  CLISpecsSimpleCommand,
  CLISpecsSimpleCommandGroup,
  CLISpecsSimpleCommandTree,
} from "./CLIModuleGenerator";
import CommandGroupItem from "./CommandGroupItem";
import {
  calculateSelected,
  prepareLoadCommandsOfCommandGroup,
  type ProfileCTCommandGroup,
  type ProfileCTCommand,
  type ProfileCTCommandGroups,
  type ProfileCTCommandVersion,
} from "./utils/commandTreeUtils";

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
  const [defaultExpanded, _] = useState(GetDefaultExpanded(profileCommandTree));

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
    const [loadingNamesList, newTree] = PrepareLoadCommands(profileCommandTree);
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

interface ProfileCommandTree {
  name: string;
  commandGroups: ProfileCTCommandGroups;
}

const decodeProfileCTCommandVersion = (response: any): ProfileCTCommandVersion => {
  return {
    name: response.name,
    stage: response.stage,
  };
};

const decodeProfileCTCommand = (
  response: CLISpecsCommand,
  selected: boolean = false,
  modified: boolean = false,
  registered: boolean | undefined = undefined,
  selectedVersion: string | undefined = undefined,
): ProfileCTCommand => {
  const versions = response.versions?.map((value: any) => decodeProfileCTCommandVersion(value));
  const command = {
    id: response.names.join("/"),
    names: [...response.names],
    versions: versions,
    modified: modified,
    loading: false,
    selected: selected,
    registered: registered,
  };
  if (selected) {
    let version: string | undefined;
    if (selectedVersion !== undefined) {
      version = selectedVersion;
    } else {
      version = versions ? versions[0].name : undefined;
    }

    return {
      ...command,
      selectedVersion: version,
    };
  } else {
    return command;
  }
};

const getDefaultExpandedOfCommandGroup = (commandGroup: ProfileCTCommandGroup): string[] => {
  const expandedIds = commandGroup.commandGroups
    ? Object.values(commandGroup.commandGroups).flatMap((value) =>
        value.selected !== false ? [value.id, ...getDefaultExpandedOfCommandGroup(value)] : [],
      )
    : [];
  return expandedIds;
};

const GetDefaultExpanded = (tree: ProfileCommandTree): string[] => {
  return Object.values(tree.commandGroups).flatMap((value) => {
    const ids = getDefaultExpandedOfCommandGroup(value);
    if (value.selected !== false) {
      ids.push(value.id);
    }
    return ids;
  });
};

const PrepareLoadCommands = (tree: ProfileCommandTree): [string[][], ProfileCommandTree] => {
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

const initializeCommandByModView = (
  view: CLIModViewCommand | undefined,
  simpleCommand: CLISpecsSimpleCommand,
): ProfileCTCommand => {
  return {
    id: simpleCommand.names.join("/"),
    names: simpleCommand.names,
    modified: false,
    loading: false,
    selected: view !== undefined && view.version !== undefined,
    selectedVersion: view !== undefined ? view.version : undefined,
    registered: view !== undefined ? view.registered : true,
  };
};

const initializeCommandGroupByModView = (
  view: CLIModViewCommandGroup | undefined,
  simpleCommandGroup: CLISpecsSimpleCommandGroup,
): ProfileCTCommandGroup => {
  const commands =
    simpleCommandGroup.commands !== undefined
      ? Object.fromEntries(
          Object.entries(simpleCommandGroup.commands).map(([key, value]) => [
            key,
            initializeCommandByModView(view?.commands?.[key], value),
          ]),
        )
      : undefined;
  const commandGroups =
    simpleCommandGroup.commandGroups !== undefined
      ? Object.fromEntries(
          Object.entries(simpleCommandGroup.commandGroups).map(([key, value]) => [
            key,
            initializeCommandGroupByModView(view?.commandGroups?.[key], value),
          ]),
        )
      : undefined;
  const leftCommands = Object.entries(view?.commands ?? {})
    .filter(([key, _]) => commands?.[key] === undefined)
    .map(([_, value]) => value.names)
    .map((names) => "`az " + names.join(" ") + "`");
  const leftCommandGroups = Object.entries(view?.commandGroups ?? {})
    .filter(([key, _]) => commandGroups?.[key] === undefined)
    .map(([_, value]) => value.names)
    .map((names) => "`az " + names.join(" ") + "`");
  const errors = [];
  if (leftCommands.length > 0) {
    errors.push(`Miss commands in aaz: ${leftCommands.join(", ")}`);
  }
  if (leftCommandGroups.length > 0) {
    errors.push(`Miss command groups in aaz: ${leftCommandGroups.join(", ")}`);
  }
  if (errors.length > 0) {
    throw new Error(
      "\n" +
        errors.join("\n") +
        "\nSee: https://azure.github.io/aaz-dev-tools/pages/usage/cli-generator/#miss-command-models.",
    );
  }
  const selected = calculateSelected(commands ?? {}, commandGroups ?? {});
  return {
    id: simpleCommandGroup.names.join("/"),
    names: simpleCommandGroup.names,
    commands: commands,
    commandGroups: commandGroups,
    waitCommand: view?.waitCommand,
    loading: false,
    selected: selected,
  };
};

const InitializeCommandTreeByModView = (
  profileName: string,
  view: CLIModViewProfile | null,
  simpleTree: CLISpecsSimpleCommandTree,
): ProfileCommandTree => {
  const commandGroups = Object.fromEntries(
    Object.entries(simpleTree.root.commandGroups).map(([key, value]) => [
      key,
      initializeCommandGroupByModView(view?.commandGroups?.[key], value),
    ]),
  );
  const leftCommandGroups = Object.entries(view?.commandGroups ?? {})
    .filter(([key, _]) => commandGroups?.[key] === undefined)
    .map(([_, value]) => value.names)
    .map((names) => "`az " + names.join(" ") + "`");
  if (leftCommandGroups.length > 0) {
    throw new Error(
      `\nMiss command groups in aaz: ${leftCommandGroups.join(", ")}\nSee: https://azure.github.io/aaz-dev-tools/pages/usage/cli-generator/#miss-command-models.`,
    );
  }
  return {
    name: profileName,
    commandGroups: commandGroups,
  };
};

const ExportModViewCommand = (command: ProfileCTCommand): CLIModViewCommand | undefined => {
  if (command.selectedVersion === undefined) {
    return undefined;
  }

  return {
    names: command.names,
    registered: command.registered!,
    version: command.selectedVersion!,
    modified: command.modified,
  };
};

const ExportModViewCommandGroup = (commandGroup: ProfileCTCommandGroup): CLIModViewCommandGroup | undefined => {
  if (commandGroup.selected === false) {
    return undefined;
  }

  let commands: CLIModViewCommands | undefined = undefined;
  if (commandGroup.commands !== undefined) {
    commands = {};

    Object.values(commandGroup.commands!).forEach((value) => {
      const view = ExportModViewCommand(value);
      if (view !== undefined) {
        commands![value.names[value.names.length - 1]] = view;
      }
    });
  }

  let commandGroups: CLIModViewCommandGroups | undefined = undefined;
  if (commandGroup.commandGroups !== undefined) {
    commandGroups = {};

    Object.values(commandGroup.commandGroups!).forEach((value) => {
      const view = ExportModViewCommandGroup(value);
      if (view !== undefined) {
        commandGroups![value.names[value.names.length - 1]] = view;
      }
    });
  }
  return {
    names: commandGroup.names,
    commandGroups: commandGroups,
    commands: commands,
    waitCommand: commandGroup.waitCommand,
  };
};

const ExportModViewProfile = (tree: ProfileCommandTree): CLIModViewProfile => {
  const commandGroups: CLIModViewCommandGroups = {};

  Object.values(tree.commandGroups).forEach((value) => {
    const view = ExportModViewCommandGroup(value);
    if (view !== undefined) {
      commandGroups[value.names[value.names.length - 1]] = view;
    }
  });

  return {
    name: tree.name,
    commandGroups: commandGroups,
  };
};

export default CLIModGeneratorProfileCommandTree;

export type { ProfileCommandTree };

export { InitializeCommandTreeByModView, ExportModViewProfile };
