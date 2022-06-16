import TreeView from '@mui/lab/TreeView';
import TreeItem from '@mui/lab/TreeItem';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { Checkbox, FormControlLabel } from '@mui/material';

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
    selectedArgIds: string[],
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
            isSelected: false,
        }
        if (arg.indexes.length > 1) {
            arg.display = `[${arg.var}] ${arg.indexes.map(idx => {
                if (idx[1] === '.' || idx[1] === '[' || idx[1] === '{') {
                    return `-${idx}`;
                } else {
                    return `--${idx}`;
                }
            }).join(' ')}`;
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


function BuildArgSimilarTree(response: any): {tree: ArgSimilarTree, expandedIds: string[]} {
    const tree = {
        root: decodeResponseArgSimilarGroup(response.data.aaz, 'az'),
        selectedArgIds: [],
    };
    const expandedIds = gatherNodeIds(tree.root);
    const newTree = updateSelectionStateForArgSimilarTree(tree, new Set<string>([tree.root.id]));
    return {
        tree: newTree,
        expandedIds:  expandedIds,
    };
}

function updateSelectionStateForArgSimilarCommand(command: ArgSimilarCommand, selectedIds: Set<string>): {command: ArgSimilarCommand, selectedArgIds: string[]} {
    let newSelectedIds: string[] = [];
    let newCommand = {
        ...command,
        args: command.args.map(arg => {
            let isSelected = selectedIds.has(arg.id);
            if (!isSelected) {
                const idParts = arg.id.split('/');
                for (let idx = 1; idx < idParts.length; idx += 1) {
                    let newId = idParts.slice(0, idx+1).join('/');
                    if (selectedIds.has(newId)) {
                        isSelected = true;
                        break;
                    }
                }
            }
            if (isSelected === true) {
                newSelectedIds.push(arg.id);
            }

            let newArg: ArgSimilarArg = {
                ...arg,
                indexes: [...arg.indexes],
                isSelected: isSelected,
            }
            return newArg
        }),
    }

    newCommand.selectedCount = newSelectedIds.length
    
    return {
        command: newCommand,
        selectedArgIds: newSelectedIds,
    };
}

function updateSelectionStateForArgSimilarGroup(group: ArgSimilarGroup, selectedIds: Set<string>): {group: ArgSimilarGroup, selectedArgIds: string[]} {
    let newSelectedIds: string[] = [];
    let newGroup = {
        ...group,
        groups: group.groups?.map(subGroup => {
            const {group: newSubGroup, selectedArgIds: subSelectedIds} = updateSelectionStateForArgSimilarGroup(subGroup, selectedIds);
            newSelectedIds = [...newSelectedIds, ...subSelectedIds];
            return newSubGroup;
        }),
        commands: group.commands?.map(command => {
            const {command: newCommand, selectedArgIds: subSelectedIds} = updateSelectionStateForArgSimilarCommand(command, selectedIds);
            newSelectedIds = [...newSelectedIds, ...subSelectedIds];
            return newCommand;
        }),
        
    }

    newGroup.selectedCount = newSelectedIds.length;

    return {
        group: newGroup,
        selectedArgIds: newSelectedIds,
    };
}

function updateSelectionStateForArgSimilarTree(tree: ArgSimilarTree, selectedIds: Set<string>): ArgSimilarTree {
    const {group, selectedArgIds} = updateSelectionStateForArgSimilarGroup(tree.root, selectedIds);
    return {
        root: group,
        selectedArgIds: selectedArgIds,
    }
}

function WSECArgumentSimilarPicker(props: {
    tree: ArgSimilarTree,
    expandedIds: string[],
    updatedIds: string[],
    onTreeUpdated: (tree: ArgSimilarTree) => void,
    onToggle: (nodeIds: string[]) => void
}) {

    const onCheckItem = (itemId: string, select: boolean) => {
        let selectedIds: Set<string>;
        if (select) {
            selectedIds = new Set(props.tree.selectedArgIds).add(itemId);
        } else {
            selectedIds = new Set(props.tree.selectedArgIds.filter(id => id !== itemId && !id.startsWith(`${itemId}/`)));
        }
        props.onTreeUpdated(updateSelectionStateForArgSimilarTree(props.tree, selectedIds));
    }

    const onNodeToggle = (event: React.SyntheticEvent, nodeIds: string[]) => {
        props.onToggle(nodeIds);
        event.stopPropagation();
        event.preventDefault();
    }

    const renderArg = (arg: ArgSimilarArg) => {
        const isUpdated = props.updatedIds.indexOf(arg.id) !== -1
        return (
            <TreeItem key={arg.id} nodeId={arg.id} color='inherit'
                label={
                    <FormControlLabel
                        control={<Checkbox
                            size="small"
                            checked={arg.isSelected}
                            onClick={(event) => {
                                onCheckItem(arg.id, !arg.isSelected)
                                event.stopPropagation();
                                event.preventDefault();
                            }}
                            disabled={isUpdated}
                        />}
                        label={arg.display}
                        sx={{
                            paddingLeft: 1
                        }}
                    />
                }
            />
        )
    }

    const renderCommand = (command: ArgSimilarCommand) => {
        return (
            <TreeItem key={command.id} nodeId={command.id} color='inherit'
                label={
                    <FormControlLabel
                        control={<Checkbox size="small"
                            checked={command.selectedCount > 0 && command.selectedCount === command.total}
                            indeterminate={command.selectedCount > 0 && command.selectedCount < command.total}
                            onClick={(event) => {
                                onCheckItem(command.id, !(command.selectedCount > 0 && command.selectedCount === command.total))
                                event.stopPropagation();
                                event.preventDefault();
                            }}
                        />}
                        label={command.name}
                        sx={{
                            paddingLeft: 1
                        }}
                    />
                }
            >
                {Array.isArray(command.args) ? command.args.map((arg) => renderArg(arg)) : null}
            </TreeItem>
        )
    }

    const renderGroup = (group: ArgSimilarGroup) => {
        return (
            <TreeItem key={group.id} nodeId={group.id} color='inherit'
                label={
                    <FormControlLabel
                        control={<Checkbox size="small"
                            checked={group.selectedCount > 0 && group.selectedCount === group.total}
                            indeterminate={group.selectedCount > 0 && group.selectedCount < group.total}
                            onClick={(event) => {
                                onCheckItem(group.id, !(group.selectedCount > 0 && group.selectedCount === group.total))
                                event.stopPropagation();
                                event.preventDefault();
                            }}
                        />}
                        label={group.name}
                        sx={{
                            paddingLeft: 1
                        }}
                    />
                }
            >
                {Array.isArray(group.commands) ? group.commands.map((command) => renderCommand(command)) : null}
                {Array.isArray(group.groups) ? group.groups.map((subGroup) => renderGroup(subGroup)) : null}
            </TreeItem>
        )
    }

    return (<>
        <TreeView
            sx={{
                flexGrow: 1,
                overflowY: 'auto',
            }}
            defaultCollapseIcon={<ExpandMoreIcon />}
            defaultExpandIcon={<ChevronRightIcon />}
            onNodeToggle={onNodeToggle}
            selected={[]}
            expanded={props.expandedIds}
        >
            {renderGroup(props.tree.root)}
        </TreeView>
    </>)
}

export default WSECArgumentSimilarPicker;
export { BuildArgSimilarTree };
export type { ArgSimilarTree, ArgSimilarGroup, ArgSimilarCommand, ArgSimilarArg }