import {
  CLIModViewCommand,
  CLIModViewCommandGroup,
  CLIModViewCommandGroups,
  CLIModViewCommands,
  CLIModViewProfile,
} from "../interfaces";
import {
  CLISpecsCommand,
  CLISpecsSimpleCommand,
  CLISpecsSimpleCommandGroup,
  CLISpecsSimpleCommandTree,
} from "../components/CLIModuleGenerator";
import {
  calculateSelected,
  type ProfileCTCommandGroup,
  type ProfileCTCommand,
  type ProfileCTCommands,
  type ProfileCTCommandGroups,
  type ProfileCTCommandVersion,
} from "./commandTreeUtils";

export interface ProfileCommandTree {
  name: string;
  commandGroups: ProfileCTCommandGroups;
  // commands generated in the module but missing in local aaz repo
  missingInAaz?: string[];
}

export const decodeProfileCTCommandVersion = (response: any): ProfileCTCommandVersion => {
  return {
    name: response.name,
    stage: response.stage,
  };
};

export const decodeProfileCTCommand = (
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
    let missingVersionInAaz: string | undefined;
    if (selectedVersion !== undefined && versions?.some((value) => value.name === selectedVersion)) {
      version = selectedVersion;
    } else {
      version = versions ? versions[0].name : undefined;
      missingVersionInAaz = selectedVersion;
    }

    return {
      ...command,
      selectedVersion: version,
      missingVersionInAaz: missingVersionInAaz,
    };
  } else {
    return command;
  }
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

const collectMissingInAaz = (
  view: { commands?: CLIModViewCommands; commandGroups?: CLIModViewCommandGroups } | undefined,
  commands: ProfileCTCommands | undefined,
  commandGroups: ProfileCTCommandGroups | undefined,
  missingInAaz: string[],
) => {
  Object.entries(view?.commands ?? {})
    .filter(([key]) => commands?.[key] === undefined)
    .forEach(([, value]) => missingInAaz.push("az " + value.names.join(" ")));
  Object.entries(view?.commandGroups ?? {})
    .filter(([key]) => commandGroups?.[key] === undefined)
    .forEach(([, value]) => missingInAaz.push("az " + value.names.join(" ")));
};

const initializeCommandGroupByModView = (
  view: CLIModViewCommandGroup | undefined,
  simpleCommandGroup: CLISpecsSimpleCommandGroup,
  missingInAaz: string[],
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
            initializeCommandGroupByModView(view?.commandGroups?.[key], value, missingInAaz),
          ]),
        )
      : undefined;
  collectMissingInAaz(view, commands, commandGroups, missingInAaz);
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

export const initializeCommandTreeByModView = (
  profileName: string,
  view: CLIModViewProfile | null,
  simpleTree: CLISpecsSimpleCommandTree,
): ProfileCommandTree => {
  const missingInAaz: string[] = [];
  const commandGroups = Object.fromEntries(
    Object.entries(simpleTree.root.commandGroups).map(([key, value]) => [
      key,
      initializeCommandGroupByModView(view?.commandGroups?.[key], value, missingInAaz),
    ]),
  );
  collectMissingInAaz(view ?? undefined, undefined, commandGroups, missingInAaz);
  return {
    name: profileName,
    commandGroups: commandGroups,
    missingInAaz: missingInAaz,
  };
};

const collectMissingVersionsOfCommandGroup = (group: ProfileCTCommandGroup, missing: string[]) => {
  Object.values(group.commands ?? {}).forEach((command) => {
    if (command.selected && command.missingVersionInAaz !== undefined) {
      missing.push(`az ${command.names.join(" ")} (${command.missingVersionInAaz} -> ${command.selectedVersion})`);
    }
  });
  Object.values(group.commandGroups ?? {}).forEach((subGroup) =>
    collectMissingVersionsOfCommandGroup(subGroup, missing),
  );
};

// versions generated in the module but missing in local aaz repo, they are replaced by the latest aaz version
export const collectMissingVersionsInAaz = (tree: ProfileCommandTree): string[] => {
  const missing: string[] = [];
  Object.values(tree.commandGroups).forEach((group) => collectMissingVersionsOfCommandGroup(group, missing));
  return missing;
};

const exportModViewCommand = (command: ProfileCTCommand): CLIModViewCommand | undefined => {
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

const exportModViewCommandGroup = (commandGroup: ProfileCTCommandGroup): CLIModViewCommandGroup | undefined => {
  if (commandGroup.selected === false) {
    return undefined;
  }

  let commands: CLIModViewCommands | undefined = undefined;
  if (commandGroup.commands !== undefined) {
    commands = {};

    Object.values(commandGroup.commands!).forEach((value) => {
      const view = exportModViewCommand(value);
      if (view !== undefined) {
        commands![value.names[value.names.length - 1]] = view;
      }
    });
  }

  let commandGroups: CLIModViewCommandGroups | undefined = undefined;
  if (commandGroup.commandGroups !== undefined) {
    commandGroups = {};

    Object.values(commandGroup.commandGroups!).forEach((value) => {
      const view = exportModViewCommandGroup(value);
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

export const exportModViewProfile = (tree: ProfileCommandTree): CLIModViewProfile => {
  const commandGroups: CLIModViewCommandGroups = {};

  Object.values(tree.commandGroups).forEach((value) => {
    const view = exportModViewCommandGroup(value);
    if (view !== undefined) {
      commandGroups[value.names[value.names.length - 1]] = view;
    }
  });

  return {
    name: tree.name,
    commandGroups: commandGroups,
  };
};
