import TreeView from '@mui/lab/TreeView';
import TreeItem from '@mui/lab/TreeItem';

interface ArgSimilarArg {
    id: string,
    var: string,
    display: string,
    indexes: string[],
    isSelected: boolean,
}

interface ArgSimilarCommand {
    id: string,
    name: string,
    args: ArgSimilarArg[],
    total: number,
    selectedCount: number,
}

interface ArgSimilarGroup {
    id: string,
    name: string,
    groups?: ArgSimilarGroup[],
    commands?: ArgSimilarCommand[],
    total: number,
    selectedCount: number,
}

interface ArgSimilarTree {
    root: ArgSimilarGroup,
    expandedIds: string[],
}

interface ResponseArgSimilarCommand {
    id: string,
    args: {
        [argVar: string]: string[],
    }
}

interface ResponseArgSimilarGroup {
    id: string,
    commandGroups?: {
        [name: string]: ResponseArgSimilarGroup
    },
    commands?: {
        [name: string]: ResponseArgSimilarCommand
    }
}


function decodeResponseArgSimilarCommand(responseCommand: ResponseArgSimilarCommand, commandName: string): ArgSimilarCommand {
    let command: ArgSimilarCommand = {
        id: responseCommand.id,
        name: commandName,
        args: [],
        total: 0,
        selectedCount: 0,
    }
    for (const argVar in responseCommand.args) {
        const arg: ArgSimilarArg = {
            id: `${command.id}/Arguments/${argVar}`,
            var: argVar,
            indexes: responseCommand.args[argVar],
            display: "",
            isSelected: true,
        }
        if (arg.indexes.length > 1) {
            arg.display = `[${arg.var}] ${arg.indexes.join('; ')}`;
        } else if (arg.indexes.length == 1) {
            let idx = arg.indexes[0];
            if (idx[1] === '.' || idx[1] === '[' || idx[1] === '{') {
                arg.display = `-${idx}`;
            } else {
                arg.display = `--${idx}`;
            }
        }
        command.args.push(arg);
    }
    command.total = command.args.length;
    return command;
}

function decodeResponseArgSimilarGroup(responseGroup: ResponseArgSimilarGroup, groupName: string): ArgSimilarGroup {
    let group: ArgSimilarGroup = {
        id: responseGroup.id,
        name: groupName,
        total: 0,
        selectedCount: 0,
    }

    if (typeof responseGroup.commandGroups === 'object' && responseGroup.commandGroups !== null) {
        group.groups = [];
        for (const name in responseGroup.commandGroups) {
            const subGroup = decodeResponseArgSimilarGroup(responseGroup.commandGroups[name], name);
            group.groups.push(subGroup);
            group.total += subGroup.total;
        }
    }

    if (typeof responseGroup.commands === 'object' && responseGroup.commands !== null) {
        group.commands = [];
        for (const name in responseGroup.commands) {
            const command = decodeResponseArgSimilarCommand(responseGroup.commands[name], name);
            group.commands.push(command);
            group.total += command.total;
        }
    }
    if (group.commands === undefined && group.groups !== undefined && group.groups.length === 1) {
        group = group.groups[0]
        group.name = `${groupName} ${group.name}`
    }
    return group;
}

function gatherNodeIds(group: ArgSimilarGroup): string[] {
    let nodeIds: string[] = [group.id];
    if (group.commands !== undefined) {
        group.commands.forEach(command => {
            nodeIds.push(command.id);
        })
    }
    if (group.groups !== undefined) {
        group.groups.forEach(subGroup => {
            nodeIds = [...nodeIds, ...gatherNodeIds(subGroup)]
        })
    }
    return nodeIds;
}


function BuildArgSimilarTree(response: any): ArgSimilarTree {
    let root = decodeResponseArgSimilarGroup(response.data.aaz, 'az');
    updateSelectionStateForArgSimilarTree(root);
    return {
        root: root,
        expandedIds: gatherNodeIds(root),
    };
}

function updateSelectionStateForArgSimilarCommand(command: ArgSimilarCommand): string[] {
    command.selectedCount = 0
    let selectedIds: string[] = [];

    command.args.forEach(arg => {
        if (arg.isSelected) {
            command.selectedCount += 1;
            selectedIds.push(arg.id);
        }
    })
    return selectedIds;
}

function updateSelectionStateForArgSimilarGroup(group: ArgSimilarGroup): string[] {
    group.selectedCount = 0;
    let selectedIds: string[] = [];

    group.groups?.forEach(subGroup => {
        const subSelectedIds = updateSelectionStateForArgSimilarGroup(subGroup);
        selectedIds = [...selectedIds, ...subSelectedIds];
        group.selectedCount += subGroup.selectedCount;
    });

    group.commands?.forEach(command => {
        const subSelectedIds = updateSelectionStateForArgSimilarCommand(command);
        selectedIds = [...selectedIds, ...subSelectedIds];
        group.selectedCount += command.selectedCount;
    })
    return selectedIds;
}

function updateSelectionStateForArgSimilarTree(root: ArgSimilarGroup): string[] {
    return updateSelectionStateForArgSimilarGroup(root);
}

function SimilarArgumentView(props: {
    tree: ArgSimilarTree
}) {

    const renderArg = (arg: ArgSimilarArg) => {
        return (
            <TreeItem key={arg.id} nodeId={arg.id} label={arg.display} color='inherit'/>
        )
    }

    const renderCommand = (command: ArgSimilarCommand) => {
        return (
            <TreeItem key={command.id} nodeId={command.id} label={command.name} color='inherit'>
                 {Array.isArray(command.args) ? command.args.map((arg) => renderArg(arg)) : null}
            </TreeItem>
        )
    }

    const renderGroup = (group: ArgSimilarGroup) => {
        return (
            <TreeItem key={group.id} nodeId={group.id} label={group.name} color='inherit'>
                {Array.isArray(group.commands) ? group.commands.map((command) => renderCommand(command)) : null}
                {Array.isArray(group.groups) ? group.groups.map((subGroup) => renderGroup(subGroup)) : null}
            </TreeItem>
        )
    }

    return (<>
        <TreeView sx={{
            flexGrow: 1,
            overflowY: 'auto',
        }}
        expanded={props.tree.expandedIds}
        >
            {renderGroup(props.tree.root)}
        </TreeView>
    </>)
}

export default SimilarArgumentView;
export { BuildArgSimilarTree };
export type { ArgSimilarTree, ArgSimilarGroup, ArgSimilarCommand, ArgSimilarArg }