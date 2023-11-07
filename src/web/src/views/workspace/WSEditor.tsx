import * as React from 'react';
import { Box, Dialog, Slide, Drawer, Toolbar, DialogTitle, DialogContent, DialogActions, LinearProgress, Button, List, ListSubheader, Paper, ListItemButton, ListItemIcon, Checkbox, ListItemText, ListItem, TextField, Alert, InputLabel, IconButton, Input, Typography, TypographyProps } from '@mui/material';
import { useParams } from 'react-router';
import axios from 'axios';
import { TransitionProps } from '@mui/material/transitions';
import WSEditorSwaggerPicker from './WSEditorSwaggerPicker';
import WSEditorToolBar from './WSEditorToolBar';
import WSEditorCommandTree, { CommandTreeLeaf, CommandTreeNode } from './WSEditorCommandTree';
import WSEditorCommandGroupContent, { CommandGroup, DecodeResponseCommandGroup, ResponseCommandGroup, ResponseCommandGroups } from './WSEditorCommandGroupContent';
import WSEditorCommandContent, { Command, Resource, DecodeResponseCommand, ResponseCommand } from './WSEditorCommandContent';
import DoDisturbOnRoundedIcon from '@mui/icons-material/DoDisturbOnRounded';
import AddCircleRoundedIcon from '@mui/icons-material/AddCircleRounded';
import { styled } from '@mui/system';

interface CommandGroupMap {
    [id: string]: CommandGroup
}

interface CommandMap {
    [id: string]: Command
}

interface ClientEndpointTemplate {
    cloud: string,
    template: string,
}

interface ClientTemplateMap {
    [cloud: string]: string
}

interface ClientAADAuth {
    scopes: string[],
}

interface ClientAuth {
    aad: ClientAADAuth,
}

interface ClientConfig {
    version: string,
    templates: ClientTemplateMap,
    auth: ClientAuth,
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
    clientConfigurable: boolean,

    selected: Command | CommandGroup | null,
    reloadTimestamp: number | null,
    expanded: Set<string>,

    commandMap: CommandMap,
    commandGroupMap: CommandGroupMap,
    commandTree: CommandTreeNode[],

    showSwaggerResourcePicker: boolean,
    showSwaggerReloadDialog: boolean,
    showClientConfigDialog: boolean,
    showExportDialog: boolean,
    showDeleteDialog: boolean,
    showModifyDialog: boolean,
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
            clientConfigurable: false,
            selected: null,
            reloadTimestamp: null,
            expanded: new Set<string>(),
            commandMap: {},
            commandGroupMap: {},
            commandTree: [],
            showSwaggerResourcePicker: false,
            showSwaggerReloadDialog: false,
            showClientConfigDialog: false,
            showExportDialog: false,
            showDeleteDialog: false,
            showModifyDialog: false,
        }
    }

    componentDidMount() {
        this.loadWorkspace();
    }

    loadWorkspace = async (preSelectedId?: string | null) => {
        const { workspaceUrl } = this.state
        if (preSelectedId === undefined) {
            preSelectedId = this.state.selected?.id;
        }

        try {
            let res = await axios.get(`/AAZ/Specs/Planes`);
            let planeNames: String[] = res.data.map((v: any) => {
                return v.name
            });
            res = await axios.get(workspaceUrl);
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

            if (preSelectedId != null) {
                if (preSelectedId.startsWith('command:')) {
                    let id: string = preSelectedId;
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
                } else if (preSelectedId.startsWith('group:')) {
                    let id_1: string = preSelectedId;
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

            // when the plane name not included in the built-in planes, it is a client configurable plane
            const clientConfigurable = !planeNames.includes(res.data.plane);
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
                    clientConfigurable: clientConfigurable,
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
                        newExpanded.add(expandedIdParts.slice(0, idx + 1).join('/'));
                    })
                    return {
                        ...preState,
                        expanded: newExpanded,
                    }
                })
            }

            if (clientConfigurable) {
                const clientConfig = await this.getWorkspaceClientConfig(workspaceUrl);
                if (clientConfig == null) {
                    this.showClientConfigDialog();
                    return;
                }
            }

            if (commandTree.length === 0) {
                this.showSwaggerResourcePicker();
            }
        } catch (err) {
            return console.error(err);
        }
    }

    getWorkspaceClientConfig = async (workspaceUrl: string) => {
        try {
            let res = await axios.get(`${workspaceUrl}/ClientConfig`);
            const clientConfig: ClientConfig = {
                version: res.data.version,
                templates: {},
                auth: res.data.auth,
            }
            res.data.endpoints.templates.forEach((value: any) => {
                clientConfig.templates[value.cloud] = value.template;
            });
            return clientConfig;
        } catch (err: any) {
            // catch 404 error
            if (err.response?.status === 404) {
                return null;
            }
        }
    }

    showClientConfigDialog = () => {
        this.setState({ showClientConfigDialog: true })
    }

    showSwaggerResourcePicker = () => {
        this.setState({ showSwaggerResourcePicker: true })
    }

    showSwaggerReloadDialog = () => {
        this.setState({ showSwaggerReloadDialog: true })
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

    handleBackToHomepage = (blank: boolean) => {
        if (blank) {
            window.open('/?#/workspace', "_blank");
        } else {
            window.location.href = '/?#/workspace';
        }
    }

    handleGenerate = () => {
        this.setState({
            showExportDialog: true
        })
    }

    handleGenerationClose = (exported: boolean, showClientConfigDialog: boolean) => {
        this.setState({
            showExportDialog: false
        })
        if (showClientConfigDialog) {
            this.setState({
                showClientConfigDialog: true
            })
        }
    }

    handleDelete = () => {
        this.setState({
            showDeleteDialog: true
        })
    }

    handleDeleteClose = (deleted: boolean) => {
        this.setState({
            showDeleteDialog: false
        })
        if (deleted) {
            this.handleBackToHomepage(false);
        }
    }

    handleModify = () => {
        this.setState({
            showModifyDialog: true
        })
    }

    handleModifyClose = (newWSName: string | null) => {
        this.setState({
            showModifyDialog: false
        })
        if (!newWSName) {
            return;
        }
        setTimeout(() => {
            const target_url = `/?#/workspace/` + newWSName;
            window.location.href = target_url;
            window.location.reload();
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
        this.loadWorkspace(commandGroup?.id);
    }

    handleCommandUpdate = (command: Command | null) => {
        this.loadWorkspace(command?.id);
    }

    handleCommandTreeToggle = (nodeIds: string[]) => {
        const newExpanded = new Set(nodeIds);
        this.setState({
            expanded: newExpanded,
        });
    }

    handleClientConfigDialogClose = (updated: boolean) => {
        this.setState({
            showClientConfigDialog: false
        })
        if (updated) {
            this.loadWorkspace();
        }
    }

    render() {
        const { showSwaggerResourcePicker, showSwaggerReloadDialog, showExportDialog, showDeleteDialog, showModifyDialog, plane, name, commandTree, selected, reloadTimestamp, workspaceUrl, expanded, showClientConfigDialog, clientConfigurable } = this.state;
        const expandedIds: string[] = []
        expanded.forEach((expandId) => {
            expandedIds.push(expandId);
        })
        return (
            <React.Fragment>
                <WSEditorToolBar workspaceName={name} onHomePage={() => { this.handleBackToHomepage(true); }} onGenerate={this.handleGenerate} onDelete={this.handleDelete} onModify={this.handleModify} >
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
                                onEditClientConfig={clientConfigurable ? this.showClientConfigDialog : undefined}
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
                                workspaceUrl={workspaceUrl} previewCommand={(selected as Command)}
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
                {showModifyDialog && <WSRenameDialog workspaceUrl={workspaceUrl} workspaceName={name} open={showModifyDialog} onClose={this.handleModifyClose} />}
                {showDeleteDialog && <WSEditorDeleteDialog workspaceName={name} open={showDeleteDialog} onClose={this.handleDeleteClose} />}
                {showExportDialog && <WSEditorExportDialog workspaceUrl={workspaceUrl} open={showExportDialog} clientConfigurable={clientConfigurable} onClose={this.handleGenerationClose} />}
                {showSwaggerReloadDialog && <WSEditorSwaggerReloadDialog workspaceUrl={workspaceUrl} open={showSwaggerReloadDialog} onClose={this.handleSwaggerReloadDialogClose} />}
                {showClientConfigDialog && <WSEditorClientConfigDialog workspaceUrl={workspaceUrl} open={showClientConfigDialog} onClose={this.handleClientConfigDialogClose} />}
            </React.Fragment>
        )
    }
}

interface WSEditorExportDialogProps {
    workspaceUrl: string,
    open: boolean,
    clientConfigurable: boolean,
    onClose: (exported: boolean, showClientConfigDialog: boolean) => void,
}

interface WSEditorExportDialogState {
    updating: boolean,
    invalidText: string | undefined,
    clientConfigOOD: boolean,
}
class WSEditorExportDialog extends React.Component<WSEditorExportDialogProps, WSEditorExportDialogState> {

    constructor(props: WSEditorExportDialogProps) {
        super(props);
        this.state = {
            updating: false,
            invalidText: undefined,
            clientConfigOOD: false,
        }
    }

    componentDidMount(): void {
        if (this.props.clientConfigurable) {
            this.verifyClientConfig();
        }
    }

    handleClose = () => {
        this.props.onClose(false, false);
    }

    verifyClientConfig = async () => {
        const url = `${this.props.workspaceUrl}/ClientConfig/AAZ/Compare`;
        this.setState({updating: true});
        try {
            await axios.post(url);
            this.setState({clientConfigOOD: false, updating: false});
        } catch (err: any) {
            // catch 409 error
            if (err.response?.status === 409) {
                this.setState({
                    invalidText: `The client config in this workspace is out of date. Please refresh it first.`,
                    clientConfigOOD: true,
                    updating: false,
                });
                return;
            } else {
                console.error(err.response)
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`,
                    });
                }
                this.setState({updating: false});
            }
        }
    }

    inheritClientConfig = async () => {
        const url = `${this.props.workspaceUrl}/ClientConfig/AAZ/Inherit`;
        this.setState({updating: true});
        try {
            await axios.post(url);
            this.setState({clientConfigOOD: false, updating: false});
            this.props.onClose(false, true);
        } catch (err: any) {
            console.error(err.response)
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`,
                });
            }
            this.setState({updating: false});
        }
    }

    handleExport = async () => {
        const url = `${this.props.workspaceUrl}/Generate`;
        this.setState({updating: true});

        try {
            await axios.post(url);
            this.setState({updating: false});
            this.props.onClose(false, false);
        } catch (err: any) {
            console.error(err.response)
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`,
                });
            }
            this.setState({updating: false});
        }
    }

    render(): React.ReactNode {
        const { updating, invalidText, clientConfigOOD } = this.state;
        return (
            <Dialog
                disableEscapeKeyDown
                open={this.props.open}
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
                        {clientConfigOOD && <Button onClick={this.inheritClientConfig}>Refresh Client Config</Button>}
                        {!clientConfigOOD && <Button onClick={this.handleClose}>Cancel</Button>}
                        {!clientConfigOOD && <Button onClick={this.handleExport}>Confirm</Button>}
                    </React.Fragment>}
                </DialogActions>
            </Dialog>
        )
    }
}

function WSEditorDeleteDialog(props: {
    workspaceName: string,
    open: boolean,
    onClose: (deleted: boolean) => void
}) {
    const [updating, setUpdating] = React.useState<boolean>(false);
    const [invalidText, setInvalidText] = React.useState<string | undefined>(undefined);
    const [confirmName, setConfirmName] = React.useState<string | undefined>(undefined);

    const handleClose = () => {
        props.onClose(false);
    }

    const handleDelete = () => {
        setUpdating(true);
        const nodeUrl = `/AAZ/Editor/Workspaces/` + props.workspaceName;
        axios.delete(nodeUrl)
            .then((res) => {
                setUpdating(false);
                props.onClose(true);
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
            })

    }

    return (
        <Dialog
            disableEscapeKeyDown
            open={props.open}
        >
            <DialogTitle>Delete '{props.workspaceName}' workspace?</DialogTitle>
            <DialogContent dividers={true}>
                {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                <TextField
                    id="name"
                    label="Workspace Name"
                    helperText="Please type workspace name to confirm."
                    type="text"
                    fullWidth
                    variant='standard'
                    value={confirmName}
                    onChange={(event: any) => {
                        setConfirmName(event.target.value)
                    }}
                    margin="normal" required
                />
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress color='info' />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleDelete} disabled={props.workspaceName !== confirmName}>Confirm</Button>
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
        const { selectedResources, resourceOptions } = this.state;
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
        const { invalidText, selectedResources, updating, resourceOptions } = this.state;

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

interface WSRenameDialogProps {
    workspaceUrl: string,
    workspaceName: string,
    open: boolean,
    onClose: (newWSName: string | null) => void
}

interface WSRenameDialogState {
    newWSName: string,
    invalidText?: string,
    updating: boolean
}

class WSRenameDialog extends React.Component<WSRenameDialogProps, WSRenameDialogState> {

    constructor(props: WSRenameDialogProps) {
        super(props);
        this.state = {
            newWSName: this.props.workspaceName,
            updating: false
        }
    }

    handleModify = (event: any) => {
        let { newWSName } = this.state;
        let { workspaceUrl, workspaceName } = this.props;

        let nName = newWSName.trim();
        if (nName.length < 1) {
            this.setState({
                invalidText: `Field 'Name' is required.`
            })
            return;
        }

        this.setState({
            invalidText: undefined
        });
        this.setState({
            updating: true,
        })

        if (workspaceName === nName) {
            this.setState({
                updating: false,
            })
            this.props.onClose(null);
        } else {
            axios.post(`${workspaceUrl}/Rename`, {
                name: nName
            }).then(res => {
                this.setState({
                    updating: false,
                })
                this.props.onClose(res.data.name);
            }).catch(err => {
                this.setState({
                    updating: false,
                })
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                    })
                }

            })
        }

    }

    handleClose = () => {
        this.setState({
            invalidText: undefined
        });
        this.props.onClose(null);
    }

    render() {
        const { invalidText, updating } = this.state;
        return (
            <Dialog
                disableEscapeKeyDown
                open={this.props.open}
                sx={{ '& .MuiDialog-paper': { width: '80%' } }}
            >
                <DialogTitle>Rename Workspace</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <TextField
                        id="name"
                        label="Name"
                        type="text"
                        fullWidth
                        variant='standard'
                        value={this.state.newWSName}
                        onChange={(event: any) => {
                            this.setState({
                                newWSName: event.target.value,
                            })
                        }}
                        margin="normal" required
                    />
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='info' />
                        </Box>
                    }
                    {!updating && <React.Fragment>
                        <Button onClick={this.handleClose}>Cancel</Button>
                        <Button onClick={this.handleModify}>Save</Button>
                    </React.Fragment>}
                </DialogActions>
            </Dialog>
        )
    }
}

interface WSEditorClientConfigDialogProps {
    workspaceUrl: string,
    open: boolean,
    onClose: (updated: boolean) => void
}

interface WSEditorClientConfigDialogState {
    updating: boolean,
    invalidText: string | undefined,
    isAdd: boolean,

    templateAzureCloud: string,
    templateAzureChinaCloud: string,
    templateAzureUSGovernment: string,
    templateAzureGermanCloud: string,
    aadAuthScopes: string[],
}


const AuthTypography = styled(Typography)<TypographyProps>(({ theme }) => ({
    color: theme.palette.primary.main,
    fontFamily: "'Roboto Condensed', sans-serif",
    fontSize: 16,
    fontWeight: 400,
}));

class WSEditorClientConfigDialog extends React.Component<WSEditorClientConfigDialogProps, WSEditorClientConfigDialogState> {

    constructor(props: WSEditorClientConfigDialogProps) {
        super(props);
        this.state = {
            updating: false,
            invalidText: undefined,
            isAdd: true,
            templateAzureCloud: "",
            templateAzureChinaCloud: "",
            templateAzureUSGovernment: "",
            templateAzureGermanCloud: "",
            aadAuthScopes: ["",],
        }
    }

    componentDidMount(): void {
        this.loadWorkspaceClientConfig();
    }

    loadWorkspaceClientConfig = async () => {
        this.setState({ updating: true });
        try {
            let res = await axios.get(`${this.props.workspaceUrl}/ClientConfig`);
            const clientConfig: ClientConfig = {
                version: res.data.version,
                templates: {},
                auth: res.data.auth,
            }
            res.data.endpoints.templates.forEach((value: any) => {
                clientConfig.templates[value.cloud] = value.template;
            });
            this.setState({
                aadAuthScopes: clientConfig.auth.aad.scopes ?? ["",],
                templateAzureCloud: clientConfig.templates['AzureCloud'] ?? "",
                templateAzureChinaCloud: clientConfig.templates['AzureChinaCloud'] ?? "",
                templateAzureUSGovernment: clientConfig.templates['AzureUSGovernment'] ?? "",
                templateAzureGermanCloud: clientConfig.templates['AzureGermanCloud'] ?? "",
                isAdd: false
            });
        } catch (err: any) {
            // catch 404 error
            if (err.response?.status === 404) {
                this.setState({
                    isAdd: true,
                });
            } else {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({ invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}` });
                }
            }
        }
        this.setState({ updating: false });
    }

    handleClose = () => {
        this.props.onClose(false);
    }

    handleUpdate = async () => {
        let { aadAuthScopes, templateAzureCloud, templateAzureChinaCloud, templateAzureGermanCloud, templateAzureUSGovernment } = this.state
        templateAzureCloud = templateAzureCloud.trim();
        if (templateAzureCloud.length < 1) {
            this.setState({
                invalidText: "Azure Cloud Endpoint Template is required."
            });
            return;
        }
        templateAzureChinaCloud = templateAzureChinaCloud.trim();
        templateAzureUSGovernment = templateAzureUSGovernment.trim();
        templateAzureGermanCloud = templateAzureGermanCloud.trim();
        // verify template url using regex, like https://{vaultName}.vault.azure.net
        const templateRegex = /^https:\/\/((\{[a-zA-Z0-9]+\})|([^{}.]+))(.((\{[a-zA-Z0-9]+\})|([^{}.]+)))*(\/)?$/;
        if (!templateRegex.test(templateAzureCloud)) {
            this.setState({
                invalidText: "Azure Cloud Endpoint Template is invalid."
            });
            return;
        }

        if (templateAzureChinaCloud.length > 0 && !templateRegex.test(templateAzureChinaCloud)) {
            this.setState({
                invalidText: "Azure China Cloud Endpoint Template is invalid."
            });
            return;
        }

        if (templateAzureUSGovernment.length > 0 && !templateRegex.test(templateAzureUSGovernment)) {
            this.setState({
                invalidText: "Azure US Government Endpoint Template is invalid."
            });
            return;
        }

        if (templateAzureGermanCloud.length > 0 && !templateRegex.test(templateAzureGermanCloud)) {
            this.setState({
                invalidText: "Azure German Cloud Endpoint Template is invalid."
            });
            return;
        }

        aadAuthScopes = aadAuthScopes.map(scope => scope.trim()).filter(scope => scope.length > 0);
        if (aadAuthScopes.length < 1) {
            this.setState({
                invalidText: "AAD Auth Scopes is required."
            });
            return;
        }

        let auth = {
            aad: {
                scopes: aadAuthScopes,
            }
        }

        let templates: ClientEndpointTemplate[] = [
            { cloud: 'AzureCloud', template: templateAzureCloud },
        ];
        if (templateAzureChinaCloud.length > 0) {
            templates.push({ cloud: 'AzureChinaCloud', template: templateAzureChinaCloud });
        }
        if (templateAzureUSGovernment.length > 0) {
            templates.push({ cloud: 'AzureUSGovernment', template: templateAzureUSGovernment });
        }
        if (templateAzureGermanCloud.length > 0) {
            templates.push({ cloud: 'AzureGermanCloud', template: templateAzureGermanCloud });
        }

        this.onUpdateClientConfig(
            templates,
            auth,
        );
    }

    onUpdateClientConfig = async (
        templates: ClientEndpointTemplate[],
        auth: ClientAuth,
    ) => {
        this.setState({ updating: true });
        try {
            await axios.post(`${this.props.workspaceUrl}/ClientConfig`, {
                templates: templates,
                auth: auth,
            });
            this.setState({ updating: false });
            this.props.onClose(true);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({ invalidText: `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}` });
            }
            this.setState({ updating: false });
        }

    }

    onRemoveAadScope = (idx: number) => {
        this.setState(preState => {
            let aadAuthScopes: string[] = [...preState.aadAuthScopes.slice(0, idx), ...preState.aadAuthScopes.slice(idx + 1)];
            if (aadAuthScopes.length === 0) {
                aadAuthScopes.push("");
            }
            return {
                ...preState,
                aadAuthScopes: aadAuthScopes,
            }
        })
    }

    onModifyAadScope = (scope: string, idx: number) => {
        this.setState(preState => {
            return {
                ...preState,
                aadAuthScopes: [...preState.aadAuthScopes.slice(0, idx), scope, ...preState.aadAuthScopes.slice(idx + 1)]
            }
        })
    }

    onAddAadScope = () => {
        this.setState(preState => {
            return {
                ...preState,
                aadAuthScopes: [...preState.aadAuthScopes, ""],
            }
        })
    }

    buildAadScopeInput = (scope: string, idx: number) => {
        return (
            <Box key={idx} sx={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'flex-start',
                ml: 1,
            }}>
                <IconButton
                    edge="start"
                    color="inherit"
                    onClick={() => this.onRemoveAadScope(idx)}
                    aria-label='remove'
                >
                    <DoDisturbOnRoundedIcon fontSize="small" />
                </IconButton>
                <Input
                    id={`aadScope-${idx}`}
                    value={scope}
                    onChange={(event: any) => {
                        this.onModifyAadScope(event.target.value, idx);
                    }}
                    sx={{ flexGrow: 1 }}
                    placeholder="Input aad auth Scope here, e.g. https://metrics.monitor.azure.com/.default"
                />

            </Box>
        )
    }

    render() {
        const { invalidText, updating, isAdd, aadAuthScopes, templateAzureCloud, templateAzureChinaCloud, templateAzureUSGovernment, templateAzureGermanCloud } = this.state;
        return (
            <Dialog
                disableEscapeKeyDown
                fullWidth={true}
                maxWidth="md"
                open={this.props.open}
            >
                <DialogTitle>{isAdd ? "Setup Client Config" : "Modify Client Config"}</DialogTitle>
                <DialogContent dividers={true}>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <InputLabel required sx={{ font: "inherit", mt: 1 }}>Endpoint Templates</InputLabel>
                    <Box sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'flex-start',
                        ml: 1,
                    }}>
                        <TextField
                            id="AzureCloud"
                            label="Azure Cloud"
                            type="text"
                            fullWidth
                            variant='standard'
                            placeholder="Endpoint template in Azure Cloud, e.g. https://{vaultName}.vault.azure.net"
                            value={templateAzureCloud}
                            onChange={(event: any) => {
                                this.setState({
                                    templateAzureCloud: event.target.value,
                                })
                            }}
                            margin='dense'
                            required
                        />

                        <TextField
                            id="AzureChinaCloud"
                            label="Azure China Cloud"
                            type="text"
                            fullWidth
                            variant='standard'
                            placeholder="Endpoint template in Azure China Cloud, e.g. https://{vaultName}.vault.azure.cn"
                            value={templateAzureChinaCloud}
                            onChange={(event: any) => {
                                this.setState({
                                    templateAzureChinaCloud: event.target.value,
                                })
                            }}
                            margin='normal'
                        />

                        <TextField
                            id="AzureUSGovernment"
                            label="Azure US Government"
                            type="text"
                            fullWidth
                            variant='standard'
                            placeholder="Endpoint template in Azure US Government, e.g. https://{vaultName}.vault.usgovcloudapi.net"
                            value={templateAzureUSGovernment}
                            onChange={(event: any) => {
                                this.setState({
                                    templateAzureUSGovernment: event.target.value,
                                })
                            }}
                            margin='normal'
                        />

                        <TextField
                            id="AzureGermanCloud"
                            label="Azure German Cloud"
                            type="text"
                            fullWidth
                            variant='standard'
                            placeholder="Endpoint template in Azure German Cloud, e.g. https://{vaultName}.vault.microsoftazure.de"
                            value={templateAzureGermanCloud}
                            onChange={(event: any) => {
                                this.setState({
                                    templateAzureGermanCloud: event.target.value,
                                })
                            }}
                            margin='normal'
                        />

                    </Box>
                    <InputLabel required sx={{ font: "inherit", mt: 1 }}>AAD Auth Scopes</InputLabel>
                    {aadAuthScopes?.map(this.buildAadScopeInput)}
                    <Box sx={{
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: 'center',
                        justifyContent: 'flex-start',
                        ml: 1,
                    }}>
                        <IconButton
                            edge="start"
                            color="inherit"
                            onClick={this.onAddAadScope}
                            aria-label='add'
                        >
                            <AddCircleRoundedIcon fontSize="small" />
                        </IconButton>
                        <AuthTypography sx={{ flexShrink: 0 }}> One more scope </AuthTypography>
                    </Box>
                </DialogContent>
                <DialogActions>
                    {updating &&
                        <Box sx={{ width: '100%' }}>
                            <LinearProgress color='info' />
                        </Box>
                    }
                    {!updating && <React.Fragment>
                        {!isAdd && <Button onClick={this.handleClose}>Cancel</Button>}
                        <Button onClick={this.handleUpdate}>Update</Button>
                    </React.Fragment>}
                </DialogActions>
            </Dialog>)
    }
}


const WSEditorWrapper = (props: any) => {
    const params = useParams()

    return <WSEditor params={params} {...props} />
}

export { WSEditorWrapper as WSEditor };
