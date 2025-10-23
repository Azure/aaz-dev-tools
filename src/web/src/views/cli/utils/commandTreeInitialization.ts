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
  type ProfileCTCommandGroups,
  type ProfileCTCommandVersion,
} from "./commandTreeUtils";

export interface ProfileCommandTree {
  name: string;
  commandGroups: ProfileCTCommandGroups;
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

export const initializeCommandTreeByModView = (
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
