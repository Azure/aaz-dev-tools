import * as React from 'react';
import { Box, Dialog, Slide, Drawer, Toolbar, DialogTitle, DialogContent, DialogActions, LinearProgress, Button, List, ListSubheader, Typography, Paper, ListItemButton, ListItemIcon, Checkbox, ListItemText, ListItem } from '@mui/material';
import { useParams } from 'react-router';
import axios from 'axios';
import { TransitionProps } from '@mui/material/transitions';
import WSEditorSwaggerPicker from './WSEditorSwaggerPicker';
import WSEditorToolBar from './WSEditorToolBar';
import WSEditorCommandTree, { CommandTreeLeaf, CommandTreeNode } from './WSEditorCommandTree';
import WSEditorCommandGroupContent, { CommandGroup, DecodeResponseCommandGroup, ResponseCommandGroup, ResponseCommandGroups } from './WSEditorCommandGroupContent';
import WSEditorCommandContent, { Command, Resource, DecodeResponseCommand, ResponseCommand } from './WSEditorCommandContent';
import { Alert } from 'reactstrap';

interface CommandGroupMap {
    [id: string]: CommandGroup
}

interface CommandMap {
    [id: string]: Command
}

interface WSEditorProps {
    params: {
        workspaceName: string
    }
}

interface WSEditorState {
    name: string
    workspaceUrl: string,
    plane: string,

    selected: Command | CommandGroup | null,
    reloadTimestamp: number | null,
    expanded: Set<string>,

    commandMap: CommandMap,
    commandGroupMap: CommandGroupMap,
    commandTree: CommandTreeNode[],

    showSwaggerResourcePicker: boolean,
    showSwaggerReloadDialog: boolean,
    showExportDialog: boolean,
    showDeleteDialog: boolean,
}

const swaggerResourcePickerTransition = React.forwardRef(function swaggerResourcePickerTransition(
    props: TransitionProps & { children: React.ReactElement },
    ref: React.Ref<unknown>
) {
    return <Slide direction='up' ref={ref} {...props} />

});

const drawerWidth = 300;


class WSEditor extends React.Component<WSEditorProps, WSEditorState> {

    constructor(props: WSEditorProps) {
        super(props);
        this.state = {
            name: this.props.params.workspaceName,
            workspaceUrl: `/AAZ/Editor/Workspaces/${this.props.params.workspaceName}`,
            plane: "",
            selected: null,
            reloadTimestamp: null,
            expanded: new Set<string>(),
            commandMap: {},
            commandGroupMap: {},
            commandTree: [],
            showSwaggerResourcePicker: false,
            showSwaggerReloadDialog: false,
            showExportDialog: false,
            showDeleteDialog: false,
        }
    }

    componentDidMount() {
        this.loadWorkspace();
    }

    loadWorkspace = async (preSelected?: CommandGroup | Command | null) => {
        const { workspaceUrl } = this.state
        if (preSelected === undefined) {
            preSelected = this.state.selected;
        }

        try {
            const res = await axios.get(workspaceUrl);
            const reloadTimestamp = Date.now();
            const commandMap: CommandMap = {};
            const commandGroupMap: CommandGroupMap = {};

            const buildCommand = (command_1: ResponseCommand): CommandTreeLeaf => {
                const cmd: Command = DecodeResponseCommand(command_1);
                commandMap[cmd.id] = cmd;
                return {
                    id: cmd.id,
                    names: [...cmd.names],
                };
            };

            const buildCommandGroup = (commandGroup_1: ResponseCommandGroup): CommandTreeNode => {
                const group: CommandGroup = DecodeResponseCommandGroup(commandGroup_1);

                commandGroupMap[group.id] = group;

                const node: CommandTreeNode = {
                    id: group.id,
                    names: [...group.names],
                    canDelete: group.canDelete,
                };

                if (typeof commandGroup_1.commands === 'object' && commandGroup_1.commands !== null) {
                    node['leaves'] = [];

                    for (const name in commandGroup_1.commands) {
                        const subLeave = buildCommand(commandGroup_1.commands[name]);
                        node['leaves'].push(subLeave);
                    }
                    node['leaves'].sort((a, b) => a.id.localeCompare(b.id));
                    if (node['leaves'].length > 0) {
                        node.canDelete = false;
                    }
                }

                if (typeof commandGroup_1.commandGroups === 'object' && commandGroup_1.commandGroups !== null) {
                    node['nodes'] = [];
                    for (const name_1 in commandGroup_1.commandGroups) {
                        const subNode = buildCommandGroup(commandGroup_1.commandGroups[name_1]);
                        node['nodes'].push(subNode);
                        if (!subNode.canDelete) {
                            node.canDelete = false;
                        }
                    }
                    node['nodes'].sort((a_1, b_1) => a_1.id.localeCompare(b_1.id));
                }

                if ((node['leaves']?.length ?? 0) > 1) {
                    node.canDelete = false
                }
                group.canDelete = node.canDelete;
                return node;
            };

            let commandTree: CommandTreeNode[] = [];

            if (res.data.commandTree.commandGroups) {
                const cmdGroups: ResponseCommandGroups = res.data.commandTree.commandGroups;
                for (const key in cmdGroups) {
                    commandTree.push(buildCommandGroup(cmdGroups[key]));
                }
                commandTree.sort((a_2, b_2) => a_2.id.localeCompare(b_2.id));
            }

            let selected: Command | CommandGroup | null = null;

            if (preSelected != null) {
                if (preSelected.id.startsWith('command:')) {
                    let id: string = preSelected.id;
                    if (id in commandMap) {
                        selected = commandMap[id];
                    } else {
                        id = 'group:' + id.slice(8);
                        let parts = id.split('/');
                        while (parts.length > 1 && !(id in commandGroupMap)) {
                            parts = parts.slice(0, -1);
                            id = parts.join('/');
                        }
                        if (id in commandGroupMap) {
                            selected = commandGroupMap[id];
                        }
                    }
                } else if (preSelected.id.startsWith('group:')) {
                    let id_1: string = preSelected.id;
                    let parts_1 = id_1.split('/');
                    while (parts_1.length > 1 && !(id_1 in commandGroupMap)) {
                        parts_1 = parts_1.slice(0, -1);
                        id_1 = parts_1.join('/');
                    }
                    if (id_1 in commandGroupMap) {
                        selected = commandGroupMap[id_1];
                    }
                }
            }

            if (selected === null && commandTree.length > 0) {
                selected = commandGroupMap[commandTree[0].id];
            }

            this.setState(preState => {
                const newExpanded = new Set<string>();

                // clean up removed group Id
                preState.expanded.forEach((value) => {
                    if (value in commandGroupMap) {
                        newExpanded.add(value);
                    }
                })

                // expand new groupId by default
                for (const groupId in commandGroupMap) {
                    if (!(groupId in preState.commandGroupMap)) {
                        newExpanded.add(groupId);
                    }
                }

                return {
                    ...preState,
                    plane: res.data.plane,
                    commandTree: commandTree,
                    selected: selected,
                    reloadTimestamp: reloadTimestamp,
                    commandMap: commandMap,
                    commandGroupMap: commandGroupMap,
                    expanded: newExpanded,
                }
            });

            if (selected) {
                let expandedId = selected.id;
                if (expandedId.startsWith('command:')) {
                    expandedId = expandedId.replace('command:', 'group:').split('/').slice(0, -1).join('/')
                }
                let expandedIdParts = expandedId.split('/');
                this.setState(preState => {
                    const newExpanded = new Set(preState.expanded);
                    expandedIdParts.forEach((value, idx) => {
                        newExpanded.add(expandedIdParts.slice(0, idx+1).join('/'));
                    })
                    return {
                        ...preState,
                        expanded: newExpanded,
                    }
                })
            }

            if (commandTree.length === 0) {
                this.showSwaggerResourcePicker();
            }
        } catch (err) {
            return console.error(err);
        }
    }

    showSwaggerResourcePicker = () => {
        this.setState({ showSwaggerResourcePicker: true })
    }

    showSwaggerReloadDialog = () => {
        this.setState({ showSwaggerReloadDialog: true})
    }

    handleSwaggerReloadDialogClose = async (reloaded: boolean) => {
        if (reloaded) {
            await this.loadWorkspace()
        }
        this.setState({
            showSwaggerReloadDialog: false
        })
    }

    handleSwaggerResourcePickerClose = (updated: boolean) => {
        if (updated) {
            this.loadWorkspace();
        }
        this.setState({
            showSwaggerResourcePicker: false
        })
    }

    handleBackToHomepage = () => {
        window.location.href = `/?#/workspace`
    }

    handleGenerate = () => {
        this.setState({
            showExportDialog: true
        })
    }

    handleGenerationClose = (exported: boolean) => {
        this.setState({
            showExportDialog: false
        })
    }

    handleDelete = () => {
        this.setState({
            showDeleteDialog: true
        })
    }

    handleDeleteClose = (exported: boolean) => {
        this.setState({
            showDeleteDialog: false
        })
    }


    handleCommandTreeSelect = (nodeId: string) => {
        if (nodeId.startsWith('command:')) {
            this.setState(preState => {
                const selected = preState.commandMap[nodeId];
                return {
                    ...preState,
                    selected: selected,
                }
            })
        } else if (nodeId.startsWith('group:')) {
            this.setState(preState => {
                const selected = preState.commandGroupMap[nodeId];
                return {
                    ...preState,
                    selected: selected,
                }
            })
        }
    }

    handleCommandGroupUpdate = (commandGroup: CommandGroup | null) => {
        this.loadWorkspace(commandGroup);
    }

    handleCommandUpdate = (command: Command | null) => {
        this.loadWorkspace(command);
    }

    handleCommandTreeToggle = (nodeIds: string[]) => {
        const newExpanded = new Set(nodeIds);
        this.setState({
            expanded: newExpanded,
        });
    }

    render() {
        const { showSwaggerResourcePicker, showSwaggerReloadDialog, showExportDialog, showDeleteDialog, plane, name, commandTree, selected, reloadTimestamp, workspaceUrl, expanded } = this.state;
        const expandedIds: string[] = []
        expanded.forEach((expandId) => {
            expandedIds.push(expandId);
        })
        return (
            <React.Fragment>
                <WSEditorToolBar workspaceName={name} onHomePage={this.handleBackToHomepage} onGenerate={this.handleGenerate} onDelete={this.handleDelete}>
                </WSEditorToolBar>

                <Box sx={{ display: 'flex' }}>
                    <Drawer
                        variant="permanent"
                        sx={{
                            width: drawerWidth,
                            flexShrink: 0,
                            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
                        }}
                    >
                        <Toolbar />
                        {selected != null &&
                            <WSEditorCommandTree
                                commandTreeNodes={commandTree}
                                onSelected={this.handleCommandTreeSelect}
                                onToggle={this.handleCommandTreeToggle}
                                onAdd={this.showSwaggerResourcePicker}
                                onReload={this.showSwaggerReloadDialog}
                                selected={selected!.id}
                                expanded={expandedIds}
                            />
                        }
                    </Drawer>

                    <Box component='main' sx={{
                        flexGrow: 1,
                        p: 1,
                    }}>
                        <Toolbar sx={{ flexShrink: 0 }} />
                        {selected != null && selected.id.startsWith('group:') &&
                            <WSEditorCommandGroupContent
                                workspaceUrl={workspaceUrl} commandGroup={(selected as CommandGroup)}
                                reloadTimestamp={reloadTimestamp!}
                                onUpdateCommandGroup={this.handleCommandGroupUpdate}
                            />
                        }
                        {selected != null && selected.id.startsWith('command:') &&
                            <WSEditorCommandContent
                                workspaceUrl={workspaceUrl} command={(selected as Command)}
                                reloadTimestamp={reloadTimestamp!}
                                onUpdateCommand={this.handleCommandUpdate}
                            />
                        }
                    </Box>
                </Box>

                <Dialog
                    fullScreen
                    open={showSwaggerResourcePicker}
                    onClose={this.handleSwaggerResourcePickerClose}
                    TransitionComponent={swaggerResourcePickerTransition}
                >
                    <WSEditorSwaggerPicker plane={plane} workspaceName={name} onClose={this.handleSwaggerResourcePickerClose} />
                </Dialog>
                {showExportDialog && <WSEditorExportDialog workspaceUrl={workspaceUrl} open={showExportDialog} onClose={this.handleGenerationClose} />}
                {showDeleteDialog && <WSEditorDeleteDialog workspaceName={name} open={showDeleteDialog} onClose={this.handleDeleteClose} onGoHome={this.handleBackToHomepage }/>}
                {showSwaggerReloadDialog && <WSEditorSwaggerReloadDialog workspaceUrl={workspaceUrl} open={showSwaggerReloadDialog} onClose={this.handleSwaggerReloadDialogClose} />}
            </React.Fragment>
        )
    }
}

function WSEditorExportDialog(props: {
    workspaceUrl: string,
    open: boolean,
    onClose: (exported: boolean) => void,
}) {
    const [updating, setUpdating] = React.useState<boolean>(false);
    const [invalidText, setInvalidText] = React.useState<string | undefined>(undefined);

    const handleClose = () => {
        props.onClose(false);
    }

    const handleExport = () => {
        const url = `${props.workspaceUrl}/Generate`;
        setUpdating(true);

        axios.post(url)
            .then(res => {
                setUpdating(false);
                props.onClose(true);
            }).catch(err => {
                console.error(err.response)
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    setInvalidText(
                        `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                    );
                }
                setUpdating(false);
            })
    }

    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
        >
            <DialogTitle>Export workspace command models to AAZ Repo</DialogTitle>
            <DialogContent>
                {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='info' />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleExport}>Confirm</Button>
                </React.Fragment>}
            </DialogActions>
        </Dialog>
    )
}

function WSEditorDeleteDialog(props: {
    workspaceName: string,
    open: boolean,
    onClose: (exported: boolean) => void
    onGoHome: (exported: boolean) => void
}) {
    const [updating, setUpdating] = React.useState<boolean>(false);
    const [invalidText, setInvalidText] = React.useState<string | undefined>(undefined);

    const handleClose = () => {
        props.onClose(false);
    }

    const handleDelete = () => {
        setUpdating(true);
        const nodeUrl = `/AAZ/Editor/Workspaces/` + props.workspaceName;
        axios.delete(nodeUrl)
            .then((res) => {
                setUpdating(false);
                props.onGoHome(true);
            })            
            .catch(err => {
                console.error(err.response.data);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    setInvalidText(
                        `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                    );
                }
                setUpdating(false);
                props.onClose(false);
        })

    }

    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
        >
            <DialogTitle>Confirm to delete workspace?</DialogTitle>
            <DialogContent>
                {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='info' />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleDelete}>Confirm</Button>
                </React.Fragment>}
            </DialogActions>
        </Dialog>
    )
}

interface WSEditorSwaggerReloadDialogProps {
    workspaceUrl: string,
    open: boolean,
    onClose: (exported: boolean) => void,
}

interface WSEditorSwaggerReloadDialogState {
    updating: boolean,
    invalidText?: string,
    resourceOptions: Resource[],
    selectedResources: Set<string>,
}

class WSEditorSwaggerReloadDialog extends React.Component<WSEditorSwaggerReloadDialogProps, WSEditorSwaggerReloadDialogState> {

    constructor(props: WSEditorSwaggerReloadDialogProps) {
        super(props);
        this.state = {
            updating: false,
            invalidText: undefined,
            resourceOptions: [],
            selectedResources: new Set(),
        }
    }
    
    componentDidMount() {
        this.loadResourceOptions();
    }

    loadResourceOptions = async () => {
        this.setState({
            invalidText: undefined,
            updating: true,
        })
        try {
            const res = await axios.get(`${this.props.workspaceUrl}/CommandTree/Nodes/aaz/Resources`)
            const resources: Resource[] = res.data;
            this.setState({
                updating: false,
                resourceOptions: resources,
                selectedResources: new Set(resources.map(resource => resource.id)),
            })
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    invalidText: `ResponseError: ${data.message!}`,
                    updating: false,
                })
            }
        }
    }

    handleClose = () => {
        this.props.onClose(false);
    }

    handleReload = async () => {
        const {selectedResources, resourceOptions} = this.state;
        const data = {
            resources: resourceOptions
            .filter(option => selectedResources.has(option.id))
            .map(option => {
                return {
                    id: option.id,
                    version: option.version,
                }
            })
        }

        const url = `${this.props.workspaceUrl}/Resources/ReloadSwagger`;
        this.setState({
            invalidText: undefined,
            updating: true,
        })
        
        try {
            await axios.post(url, data);
            this.setState({
                updating: false,
            })
            this.props.onClose(true);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    invalidText: `ResponseError: ${data.message!}`,
                    updating: false,
                })
            }
        }
    }

    onSelectedAllClick = () => {
        this.setState(preState => {
            return {
                ...preState,
                selectedResources: preState.selectedResources.size > 0 ? new Set() : new Set(preState.resourceOptions.map(op => op.id))
            }
        })
    }

    onResourceItemClick = (resourceId: string) => {
        return () => {
            this.setState(preState => {
                const selectedResources = new Set(preState.selectedResources);
                if (selectedResources.has(resourceId)) {
                    selectedResources.delete(resourceId);
                } else {
                    selectedResources.add(resourceId);
                }
                return {
                    ...preState,
                    selectedResources: selectedResources,
                }
            })
        }
    }

    render() {
        const {invalidText, selectedResources, updating, resourceOptions} = this.state;

        return (
            <Dialog
                disableEscapeKeyDown
                open={this.props.open}
                fullWidth={true}
                maxWidth="xl"
            >
                <DialogTitle>Reload Swagger Resources</DialogTitle>
                <DialogContent>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <List
                            sx={{ flexGrow: 1 }}
                            subheader={<ListSubheader>
                                <Box sx={{
                                    mt: 1,
                                    mb: 1,
                                    flexDirection: 'column',
                                    display: 'flex',
                                    alignItems: 'stretch',
                                    justifyContent: 'flex-start',
                                }} color='inherit'>
                                    {/* <Typography component='h6'>Resource Url</Typography> */}
    
                                    <Paper sx={{
                                        display: 'flex',
                                        flexDirection: 'row',
                                        alignItems: 'center',
                                        mt: 1,
                                    }} variant="outlined" square>
    
                                        <ListItemButton dense onClick={this.onSelectedAllClick} disabled={resourceOptions.length === 0}>
                                            <ListItemIcon>
                                                <Checkbox
                                                    edge="start"
                                                    checked={selectedResources.size > 0 && selectedResources.size === resourceOptions.length}
                                                    indeterminate={selectedResources.size > 0 && selectedResources.size < resourceOptions.length}
                                                    tabIndex={-1}
                                                    disableRipple
                                                    inputProps={{ 'aria-labelledby': 'SelectAll' }}
                                                />
                                            </ListItemIcon>
                                            <ListItemText id="SelectAll"
                                                primary={`All (${resourceOptions.length})`}
                                                primaryTypographyProps={{
                                                    variant: "h6",
                                                }}
                                            />
                                        </ListItemButton>
                                    </Paper>
                                </Box>
                            </ListSubheader>}
                        >
    
                            {resourceOptions.length > 0 && <Paper sx={{ ml: 2, mr: 2 }} variant="outlined" square>
                                {resourceOptions.map((option) => {
                                    const labelId = `resource-${option.id}`;
                                    const selected = selectedResources.has(option.id);
                                    return <ListItem
                                        key={option.id}
                                        sx={{
                                            display: 'flex',
                                            flexDirection: 'row',
                                            alignItems: 'center',
                                        }}
                                        disablePadding
                                    >
                                        <ListItemButton dense onClick={this.onResourceItemClick(option.id)}>
                                            <ListItemIcon>
                                                <Checkbox
                                                    edge="start"
                                                    checked={selected}
                                                    tabIndex={-1}
                                                    disableRipple
                                                    inputProps={{ 'aria-labelledby': labelId }}
                                                />
                                            </ListItemIcon>
                                            <ListItemText id={labelId}
                                                primary={`${option.version} ${option.id}`}
                                                primaryTypographyProps={{
                                                    variant: "h6",
                                                }}
                                            />
                                        </ListItemButton>
                                    </ListItem>
                                })}
                            </Paper>}
                        </List>
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='info' />
                        </Box>
                    }
                    {!updating && <React.Fragment>
                        <Button onClick={this.handleClose}>Cancel</Button>
                        <Button onClick={this.handleReload}>Reload</Button>
                    </React.Fragment>}
                </DialogActions>
            </Dialog>
        ) 
    }

}


const WSEditorWrapper = (props: any) => {
    const params = useParams()

    return <WSEditor params={params} {...props} />
}

export { WSEditorWrapper as WSEditor };
