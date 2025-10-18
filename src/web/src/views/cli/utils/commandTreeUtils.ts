interface ProfileCTCommandGroups {
  [name: string]: ProfileCTCommandGroup;
}

interface ProfileCTCommands {
  [name: string]: ProfileCTCommand;
}

interface ProfileCTCommandGroup {
  id: string;
  names: string[];
  commandGroups?: ProfileCTCommandGroups;
  commands?: ProfileCTCommands;
  waitCommand?: any;
  loading: boolean;
  selected?: boolean;
}

interface ProfileCTCommand {
  id: string;
  names: string[];
  versions?: ProfileCTCommandVersion[];
  selectedVersion?: string;
  registered?: boolean;
  modified: boolean;
  loading: boolean;
  selected: boolean;
}

interface ProfileCTCommandVersion {
  name: string;
  stage: string;
}

function calculateSelected(commands: ProfileCTCommands, commandGroups: ProfileCTCommandGroups): boolean | undefined {
  const commandsAllSelected = Object.values(commands).reduce((pre, value) => {
    return pre && value.selected;
  }, true);
  const commandsAllUnselected = Object.values(commands).reduce((pre, value) => {
    return pre && !value.selected;
  }, true);
  const commandGroupsAllSelected = Object.values(commandGroups).reduce((pre, value) => {
    return pre && value.selected === true;
  }, true);
  const commandGroupsAllUnselected = Object.values(commandGroups).reduce((pre, value) => {
    return pre && value.selected === false;
  }, true);
  if (commandsAllUnselected && commandGroupsAllUnselected) {
    return false;
  } else if (commandsAllSelected && commandGroupsAllSelected) {
    return true;
  } else {
    return undefined;
  }
}

function prepareLoadCommandsOfCommandGroup(commandGroup: ProfileCTCommandGroup): [string[][], ProfileCTCommandGroup] {
  const namesList: string[][] = [];
  const commands = commandGroup.commands
    ? Object.fromEntries(
        Object.entries(commandGroup.commands).map(([key, value]) => {
          if (value.selected === true && value.versions === undefined && value.loading === false) {
            namesList.push(value.names);
            return [
              key,
              {
                ...value,
                loading: true,
              },
            ];
          }
          return [key, value];
        }),
      )
    : undefined;
  const commandGroups = commandGroup.commandGroups
    ? Object.fromEntries(
        Object.entries(commandGroup.commandGroups).map(([key, value]) => {
          const [namesListSub, updatedGroup] = prepareLoadCommandsOfCommandGroup(value);
          namesList.push(...namesListSub);
          return [key, updatedGroup];
        }),
      )
    : undefined;
  if (namesList.length > 0) {
    return [
      namesList,
      {
        ...commandGroup,
        commands: commands,
        commandGroups: commandGroups,
      },
    ];
  } else {
    return [[], commandGroup];
  }
}

export { calculateSelected, prepareLoadCommandsOfCommandGroup };

export type {
  ProfileCTCommandGroup,
  ProfileCTCommand,
  ProfileCTCommandGroups,
  ProfileCTCommands,
  ProfileCTCommandVersion,
};
