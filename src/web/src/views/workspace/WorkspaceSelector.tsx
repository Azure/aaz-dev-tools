import { Box, Autocomplete, createFilterOptions, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Button, InputLabel, Alert } from '@mui/material';
import axios from 'axios';
import * as React from 'react';
import { Url } from 'url';
import { SwaggerItemSelector } from './WSEditorSwaggerPicker';
import styled from '@emotion/styled';
import { Plane } from './WSEditorCommandContent';


interface Workspace {
    name: string,
    plane: string | null,
    modNames: string | null,
    resourceProvider: string | null,
    lastModified: Date | null,
    url: Url | null,
    folder: string | null,
}

interface WorkspaceSelectorProps {
    name: string,
}

interface WorkspaceSelectorState {
    options: any[],
    value: Workspace | null,
    openDialog: boolean,
    newWorkspaceName: string,
}

interface InputType {
    inputValue: string,
    title: string,
}

const filter = createFilterOptions<Workspace | InputType>();


class WorkspaceSelector extends React.Component<WorkspaceSelectorProps, WorkspaceSelectorState> {

    constructor(props: WorkspaceSelectorProps) {
        super(props);
        this.state = {
            options: [],
            value: null,
            openDialog: false,
            newWorkspaceName: "",
        }
    }

    componentDidMount() {
        this.loadWorkspaces();
    }

    loadWorkspaces = async () => {
        try {
            const res = await axios.get("/AAZ/Editor/Workspaces");
            const options = res.data.map((option: any) => {
                return {
                    name: option.name,
                    lastModified: new Date(option.updated * 1000),
                    url: option.url,
                    plane: option.plane,
                    folder: option.folder
                }
            });
            this.setState({
                options: options
            })
        } catch (err: any) {
            console.error(err.response);
        }
    }

    handleDialogClose = (value: any | null) => {
        this.setState({
            newWorkspaceName: "",
            openDialog: false,
        })
        if (value != null) {
            this.onValueUpdated(value);
        }
    }

    onValueUpdated = (value: any) => {
        this.setState({
            value: value
        });
        if (value.url) {
            window.location.href = `/?#/workspace/${value.name}`
        }
    }

    render() {
        const { options, value, openDialog, newWorkspaceName } = this.state
        const { name } = this.props
        return (
            <React.Fragment>
                <Autocomplete
                    id="workspace-select"
                    value={value}
                    sx={{ width: 280 }}
                    options={options}
                    autoHighlight
                    onChange={(_event, newValue: any) => {
                        if (typeof newValue === 'string') {
                            // timeout to avoid instant validation of the dialog's form.
                            setTimeout(() => {
                                this.setState({
                                    openDialog: true,
                                    newWorkspaceName: newValue,
                                })
                            });
                        } else if (newValue && newValue.inputValue) {
                            this.setState({
                                openDialog: true,
                                newWorkspaceName: newValue.inputValue,
                            })
                        } else {
                            this.onValueUpdated(newValue);
                        }
                    }}
                    filterOptions={(options, params: any) => {
                        const filtered = filter(options, params);
                        if (params.inputValue !== '' && -1 === options.findIndex((e) => e.name === params.inputValue)) {
                            filtered.push({
                                inputValue: params.inputValue,
                                title: `Create "${params.inputValue}"`,
                            });
                        }
                        return filtered;
                    }}
                    getOptionLabel={(option) => {
                        if (typeof option === "string") {
                            return option;
                        }
                        if (option.title) {
                            return option.title;
                        }
                        return option.name;
                    }}
                    renderOption={(props, option) => {
                        const labelName = (option && option.title) ? option.title : option.name;
                        return (
                            <Box component='li'
                                {...props}
                            >
                                {labelName}
                            </Box>
                        )
                    }}
                    selectOnFocus
                    clearOnBlur
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label={name}
                            inputProps={{
                                ...params.inputProps,
                                autoComplete: 'new-password', // disable autocomplete and autofill
                            }}
                        />
                    )}
                />
                {openDialog && <WorkspaceCreateDialog openDialog={openDialog} onClose={this.handleDialogClose} name={newWorkspaceName} />}
            </React.Fragment>
        )
    }
}

interface WorkspaceCreateDialogProps {
    openDialog: boolean,
    name: string,
    onClose: (value: any | null) => void,
}

interface WorkspaceCreateDialogState {
    loading: boolean,

    invalidText?: string,
    workspaceName: string,

    planes: Plane[],
    planeOptions: string[],
    selectedPlane: string | null,

    moduleOptions: string[],
    moduleOptionsCommonPrefix: string,
    selectedModule: string | null,

    resourceProviderOptions: string[],
    resourceProviderOptionsCommonPrefix: string,
    selectedResourceProvider: string | null,

}

class WorkspaceCreateDialog extends React.Component<WorkspaceCreateDialogProps, WorkspaceCreateDialogState> {

    constructor(props: WorkspaceCreateDialogProps) {
        super(props);
        this.state = {
            loading: false,
            invalidText: undefined,
            workspaceName: props.name,

            planes: [],
            planeOptions: [],
            selectedPlane: null,

            moduleOptions: [],
            moduleOptionsCommonPrefix: '',
            selectedModule: null,

            resourceProviderOptions: [],
            resourceProviderOptionsCommonPrefix: '',
            selectedResourceProvider: null,
        }
    }

    componentDidMount(): void {
        this.loadPlanes().then(async () => {
            await this.onPlaneSelectorUpdate(this.state.planes[0].name);
        })
    }

    loadPlanes = async () => {
        try {
            this.setState({
                loading: true
            });

            const res = await axios.get(`/AAZ/Specs/Planes`);
            const planes: Plane[] = res.data.map((v: any) => {
                return {
                    name: v.name,
                    displayName: v.displayName,
                    moduleOptions: undefined,
                }
            })
            const planeOptions: string[] = res.data.map((v: any) => v.displayName)
            this.setState({
                planes: planes,
                planeOptions: planeOptions,
                loading: false
            })
            await this.onPlaneSelectorUpdate(planeOptions[0]);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    loading: false,
                    invalidText: `ResponseError: ${data.message!}`,
                })
            }
        }
    }

    onPlaneSelectorUpdate = async (planeDisplayName: string | null) => {
        const plane = this.state.planes.find((v) => v.displayName === planeDisplayName) ?? null;
        if (this.state.selectedPlane !== (plane?.displayName ?? null)) {
            if (!plane) {
                return
            }
            this.setState({
                selectedPlane: plane?.displayName ?? null,
            })
            await this.loadSwaggerModules(plane);
        } else {
            this.setState({
                selectedPlane: plane?.displayName ?? null
            })
        }
    }

    loadSwaggerModules = async (plane: Plane | null) => {
        if (plane !== null) {
            if (plane!.moduleOptions?.length) {
                this.setState({
                    moduleOptions: plane!.moduleOptions!,
                    moduleOptionsCommonPrefix: `/Swagger/Specs/${plane!.name}/`,
                })
                await this.onModuleSelectionUpdate(null);
            } else {
                try {
                    this.setState({
                        loading: true
                    });
                    const res = await axios.get(`/Swagger/Specs/${plane!.name}`);
                    const options: string[] = res.data.map((v: any) => (v.url));
                    this.setState(preState => {
                        const planes = preState.planes;
                        const index = planes.findIndex((v) => v.name === plane!.name);
                        planes[index].moduleOptions = options;
                        return {
                            ...preState,
                            loading: false,
                            planes: planes,
                            moduleOptions: options,
                            moduleOptionsCommonPrefix: `/Swagger/Specs/${plane!.name}/`,
                        }
                    })
                    await this.onModuleSelectionUpdate(null);
                } catch (err: any) {
                    console.error(err.response);
                    if (err.response?.data?.message) {
                        const data = err.response!.data!;
                        this.setState({
                            loading: false,
                            invalidText: `ResponseError: ${data.message!}`,
                        })
                    }
                }
            }
        } else {
            this.setState({
                moduleOptions: [],
                moduleOptionsCommonPrefix: '',
            })
            await this.onModuleSelectionUpdate(null);
        }

    }

    onModuleSelectionUpdate = async (moduleValueUrl: string | null) => {
        if (this.state.selectedModule !== moduleValueUrl) {
            this.setState({
                selectedModule: moduleValueUrl
            });
            await this.loadResourceProviders(moduleValueUrl);
        } else {
            this.setState({
                selectedModule: moduleValueUrl
            })
        }
    }

    loadResourceProviders = async (moduleUrl: string | null) => {
        if (moduleUrl !== null) {
            try {
                this.setState({
                    loading: true
                });
                const res = await axios.get(`${moduleUrl}/ResourceProviders`);
                const options: string[] = res.data.map((v: any) => (v.url));
                const selectedResourceProvider = options.length === 1 ? options[0] : null;
                this.setState({
                    loading: false,
                    resourceProviderOptions: options,
                    resourceProviderOptionsCommonPrefix: `${moduleUrl}/ResourceProviders/`,
                });
                this.onResourceProviderUpdate(selectedResourceProvider)
            } catch (err: any) {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        loading: false,
                        invalidText: `ResponseError: ${data.message!}`,
                    })
                }
            }
        } else {
            this.setState({
                resourceProviderOptions: [],
                resourceProviderOptionsCommonPrefix: '',
            })
            this.onResourceProviderUpdate(null);
        }
    }

    onResourceProviderUpdate = (resourceProviderUrl: string | null) => {
        if (this.state.selectedResourceProvider !== resourceProviderUrl) {
            this.setState({
                selectedResourceProvider: resourceProviderUrl,
            })
        } else {
            this.setState({
                selectedResourceProvider: resourceProviderUrl
            })
        }
    }

    verifyCreate = () => {
        this.setState({ invalidText: undefined });
        let { workspaceName, selectedModule, selectedResourceProvider } = this.state;
        const { selectedPlane, planes, moduleOptionsCommonPrefix, resourceProviderOptionsCommonPrefix } = this.state;
        workspaceName = workspaceName.trim();
        if (workspaceName.length < 1) {
            this.setState({ invalidText: `'Workspace Name' is required.` });
            return undefined
        }

        const plane = planes.find((v) => v.displayName === selectedPlane)?.name ?? null;
        if (plane === null) {
            this.setState({ invalidText: `Please select 'Plane'.` });
            return undefined
        }

        selectedModule = selectedModule ? selectedModule.replace(moduleOptionsCommonPrefix, '') : null;
        if (selectedModule === null) {
            this.setState({ invalidText: `Please select 'Module'.` });
            return undefined
        }

        selectedResourceProvider = selectedResourceProvider ? selectedResourceProvider.replace(resourceProviderOptionsCommonPrefix, '') : null;
        if (selectedResourceProvider === null) {
            this.setState({ invalidText: `Please select 'Resource Provider'.` });
            return undefined
        }
        let source = "OpenAPI";
        if (selectedResourceProvider.endsWith('/TypeSpec')) {
            selectedResourceProvider = selectedResourceProvider.replace('/TypeSpec', '');
            source = "TypeSpec";
        }
        return {
            name: workspaceName,
            plane: plane,
            modNames: selectedModule,
            resourceProvider: selectedResourceProvider,
            source: source,
        }
    }


    handleCreate = async () => {
        const data = this.verifyCreate();
        if (data === undefined) {
            return;
        }
        this.setState({ loading: true });
        try {
            const res = await axios.post('/AAZ/Editor/Workspaces', data);
            const workspace = res.data;
            const value = {
                name: workspace.name,
                plane: workspace.plane,
                modNames: workspace.modNames,
                resourceProvider: workspace.resourceProvider,
                lastModified: new Date(workspace.updated * 1000),
                url: workspace.url,
                folder: workspace.folder
            }
            this.setState({ loading: false });
            this.props.onClose(value);
        } catch (err: any) {
            console.error(err.response);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    loading: false,
                    invalidText: `ResponseError: ${data.message!}`,
                })
            }
        }
    }

    handleClose = () => {
        this.props.onClose(null);
    }

    render(): React.ReactNode {
        const { invalidText, loading, selectedPlane, selectedModule, selectedResourceProvider, workspaceName } = this.state;

        return (
            <Dialog open={this.props.openDialog}
                fullWidth={true}
                onClose={this.handleClose}
            >
                <DialogTitle>
                    Create a new workspace
                </DialogTitle>
                <DialogContent>
                    {invalidText && <Alert variant="filled" severity='error'> {invalidText} </Alert>}
                    <InputLabel shrink> API Specs</InputLabel>
                    <Box sx={{
                        mt: 1,
                        mb: 1,
                        marginLeft: 4,
                        flexDirection: 'column',
                        display: 'flex',
                        alignItems: 'stretch',
                        justifyContent: 'flex-start',
                    }}>
                        <SwaggerItemSelector
                            name="Plane"
                            commonPrefix=''
                            options={this.state.planeOptions}
                            value={selectedPlane}
                            onValueUpdate={this.onPlaneSelectorUpdate}
                        />
                        <MiddlePadding />
                        <SwaggerItemSelector
                            name="Module"
                            commonPrefix={this.state.moduleOptionsCommonPrefix}
                            options={this.state.moduleOptions}
                            value={selectedModule}
                            onValueUpdate={this.onModuleSelectionUpdate}
                        />
                        <MiddlePadding />
                        <SwaggerItemSelector
                            name="Resource Provider"
                            commonPrefix={this.state.resourceProviderOptionsCommonPrefix}
                            options={this.state.resourceProviderOptions}
                            value={selectedResourceProvider}
                            onValueUpdate={this.onResourceProviderUpdate}
                        />
                    </Box>
                    <TextField
                        fullWidth={true}
                        margin="normal"
                        id="name"
                        required
                        value={workspaceName}
                        onChange={(event: any) => {
                            this.setState({
                                workspaceName: event.target.value,
                            })
                        }}
                        label="Workspace Name"
                        type="text"
                        variant='standard'
                    />
                </DialogContent>
                <DialogActions>
                    <Box>
                        <Button onClick={this.handleClose}>Cancel</Button>
                        <Button disabled={loading || !selectedPlane || !selectedModule || !selectedResourceProvider || !workspaceName} onClick={this.handleCreate} color="success">Create</Button>
                    </Box>
                </DialogActions>
            </Dialog>
        )
    }
}

const MiddlePadding = styled(Box)(() => ({
    height: '1.5vh'
}));

export default WorkspaceSelector
