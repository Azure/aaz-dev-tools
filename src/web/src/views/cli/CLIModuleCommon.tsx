interface CLIModView {
    name: string,
    profiles: CLIModViewProfiles,
}

interface CLIModViewProfiles {
    [name: string]: CLIModViewProfile
}

interface CLIModViewProfile {
    name: string,
    commandGroups?: CLIModViewCommandGroups,
}

interface CLIModViewCommandGroups {
    [name: string]: CLIModViewCommandGroup
}

interface CLIModViewCommandGroup {
    names: string[],
    commandGroups?: CLIModViewCommandGroups,
    commands?: CLIModViewCommands,
}

interface CLIModViewCommands {
    [name: string]: CLIModViewCommand
}

interface CLIModViewCommand {
    names: string[],
    registered: boolean,
    version: string,
}

export type { CLIModView, CLIModViewProfile, CLIModViewProfiles, CLIModViewCommandGroup, CLIModViewCommandGroups, CLIModViewCommand, CLIModViewCommands }