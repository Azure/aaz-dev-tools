import * as React from 'react';
import { Typography, Box, AppBar, Toolbar, IconButton, Button, Autocomplete, TextField, Backdrop, CircularProgress, List, ListSubheader, ListItem, ListItemButton, ListItemIcon, Checkbox, ListItemText, FormControlLabel, Alert, Card, CardContent, AlertTitle, Paper, InputBase, Select, MenuItem, FormControl, InputLabel, FormHelperText } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';
import EditorPageLayout from '../../components/EditorPageLayout';
import { styled } from '@mui/material/styles';
// import SortIcon from '@mui/icons-material/Sort';


interface WSEditorSwaggerPickerProps {
    workspaceName: string,
    plane: string,
    onClose: (updated: boolean) => void
}

interface WSEditorSwaggerPickerState {
    loading: boolean

    plane: string

    // preModuleName: string | null
    // preResourceProvider: string | null
    // preVersion: string | null

    moduleOptions: string[],
    resourceProviderOptions: string[],
    versionOptions: string[],

    versionResourceIdMap: VersionResourceIdMap,
    resourceMap: ResourceMap,
    resourceOptions: Resource[],

    existingResources: Set<string>,
    selectedResources: Set<string>,
    selectedResourceInheritanceAAZVersionMap: ResourceInheritanceAAZVersionMap,
    preferredAAZVersion: string | null,

    moduleOptionsCommonPrefix: string,
    resourceProviderOptionsCommonPrefix: string,

    selectedModule: string | null,
    selectedResourceProvider: string | null,
    selectedVersion: string | null,

    updateOptions: string[],
    updateOption: string,
    invalidText?: string,
    filterText: string,
}

type ResourceVersionOperations = {
    [Named: string]: string
}

type ResourceVersion = {
    version: string
    operations: ResourceVersionOperations
    file: string
    id: string
    path: string
}

type Resource = {
    id: string
    versions: ResourceVersion[]
    aazVersions: string[] | null
}

type AAZResource = {
    id: string
    versions: string[] | null
}

type VersionResourceIdMap = {
    [version: string]: Resource[]
}

type ResourceInheritanceAAZVersionMap = {
    [id: string]: string | null
}

type ResourceMap = {
    [id: string]: Resource
}

const MiddlePadding = styled(Box)(({ theme }) => ({
    height: '2vh'
}));

const MiddlePadding2 = styled(Box)(({ theme }) => ({
    height: '8vh'
}));

const UpdateOptions = ["Generic(Get&Put) First", "Patch First", "No update command"];

class WSEditorSwaggerPicker extends React.Component<WSEditorSwaggerPickerProps, WSEditorSwaggerPickerState> {

    constructor(props: WSEditorSwaggerPickerProps) {
        super(props);
        this.state = {
            loading: false,
            invalidText: undefined,
            // preModuleName: null,
            // preResourceProvider: null,
            // preVersion: null,
            existingResources: new Set(),

            plane: this.props.plane,
            moduleOptionsCommonPrefix: '',
            resourceProviderOptionsCommonPrefix: '',
            moduleOptions: [],
            versionOptions: [],
            resourceProviderOptions: [],
            selectedResources: new Set(),
            selectedResourceInheritanceAAZVersionMap: {},
            preferredAAZVersion: null,
            resourceOptions: [],
            versionResourceIdMap: {},
            resourceMap: {},
            selectedModule: null,
            selectedResourceProvider: null,
            selectedVersion: null,
            updateOptions: UpdateOptions,
            updateOption: UpdateOptions[0],
            filterText: "",
        }
    }

    componentDidMount() {
        this.loadWorkspaceResources().then(() => {
            this.loadSwaggerModules(this.props.plane);
        })
    }

    handleClose = () => {
        this.props.onClose(false);
    }

    handleSubmit = () => {
        this.addSwagger()
    }

    loadSwaggerModules = (plane: string) => {
        axios.get(`/Swagger/Specs/${plane}`)
            .then((res) => {
                const options: string[] = res.data.map((v: any) => (v.url));
                this.setState(preState => {
                    return {
                        ...preState,
                        moduleOptions: options,
                        moduleOptionsCommonPrefix: `/Swagger/Specs/${plane}/`,
                        preModuleName: null,
                    }
                });
            })
            .catch((err) => {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        invalidText: `ResponseError: ${data.message!}`,
                    })
                }
            });
    }

    loadResourceProviders = (moduleUrl: string | null) => {
        if (moduleUrl != null) {
            axios.get(`${moduleUrl}/ResourceProviders`)
                .then((res) => {
                    const options: string[] = res.data.map((v: any) => (v.url));
                    const selectedResourceProvider = options.length === 1 ? options[0] : null;
                    this.setState({
                        resourceProviderOptions: options,
                        resourceProviderOptionsCommonPrefix: `${moduleUrl}/ResourceProviders/`
                    });
                    this.onResourceProviderUpdate(selectedResourceProvider);
                })
                .catch((err) => {
                    console.error(err.response);
                    if (err.response?.data?.message) {
                        const data = err.response!.data!;
                        this.setState({
                            invalidText: `ResponseError: ${data.message!}`,
                        })
                    }
                });
        } else {
            this.setState({
                resourceProviderOptions: [],
            })
            this.onResourceProviderUpdate(null);
        }
    }

    loadWorkspaceResources = () => {
        return axios.get(`/AAZ/Editor/Workspaces/${this.props.workspaceName}/CommandTree/Nodes/aaz/Resources`)
            .then(res => {
                const existingResources = new Set<string>();
                // let preModuleName: string | null = null;
                // let preResourceProvider: string | null = null;
                // let preVersion: string | null = null;

                if (res.data && Array.isArray(res.data) && res.data.length > 0) {
                    // const pieces = res.data[0].swagger.slice().replace(`/ResourceProviders/`, ' ').split(' ')
                    // preModuleName = `/Swagger/Specs/${pieces[0]}`;
                    // preResourceProvider = pieces[1].split('/')[0]
                    // preVersion = res.data[0].version
                    res.data.forEach(resource => {
                        existingResources.add(resource.id);
                    });
                }
                this.setState({
                    // preModuleName: preModuleName,
                    // preResourceProvider: preResourceProvider,
                    // preVersion: preVersion,
                    existingResources: existingResources,
                })
            })
            .catch((err) => {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        invalidText: `ResponseError: ${data.message!}`,
                    })
                }
            });
    }

    loadResources = async (resourceProviderUrl: string | null) => {
        if (resourceProviderUrl != null) {
            this.setState({
                invalidText: undefined,
                loading: true,
            })
            try {
                let res = await axios.get(`${resourceProviderUrl}/Resources`);
                // const resourceIdVersionMap: ResourceIdVersionMap = {}
                const versionResourceIdMap: VersionResourceIdMap = {}
                const versionOptions: string[] = []
                // const aazVersionOptions: string[] = []
                const resourceMap: ResourceMap = {}
                const resourceIdList: string[] = []
                res.data.forEach((resource: Resource) => {
                    // resource.versions.sort((a, b) =>  a.version.localeCompare(b.version));
                    resourceIdList.push(resource.id);
                    resourceMap[resource.id] = resource;
                    resourceMap[resource.id].aazVersions = null;

                    const resourceVersions = resource.versions.map((v) => v.version)
                    // resourceIdVersionMap[resource.id] = versions;
                    resourceVersions.forEach((v) => {
                        if (!(v in versionResourceIdMap)) {
                            versionResourceIdMap[v] = [];
                            versionOptions.push(v);
                        }
                        versionResourceIdMap[v].push(resource);
                    })
                })
                versionOptions.sort((a, b) => a.localeCompare(b)).reverse()
                let selectVersion = null;
                if (versionOptions.length > 0) {
                    selectVersion = versionOptions[0];
                }

                const filterBody = {
                    resources: resourceIdList
                };

                res = await axios.post(`/AAZ/Specs/Resources/${this.props.plane}/Filter`, filterBody);
                res.data.resources.forEach((aazResource: AAZResource) => {
                    if (aazResource.versions) {
                        resourceMap[aazResource.id].aazVersions = aazResource.versions;
                    }

                })
                this.setState({
                    loading: false,
                    versionResourceIdMap: versionResourceIdMap,
                    resourceMap: resourceMap,
                    versionOptions: versionOptions,
                })
                this.onVersionUpdate(selectVersion);
            } catch (err: any) {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        invalidText: `ResponseError: ${data.message!}`,
                    })
                }
            }
        } else {
            this.setState({
                versionOptions: [],
            })
            this.onVersionUpdate(null)
        }
    }

    addSwagger = () => {
        const { selectedResources, selectedVersion, selectedModule, moduleOptionsCommonPrefix, updateOption, resourceMap, selectedResourceInheritanceAAZVersionMap } = this.state;
        const resources: { id: string, options: { update_by?: string, aaz_version: string | null } }[] = [];
        selectedResources.forEach((resourceId) => {
            const res: any = {
                id: resourceId,
                options: {
                    aaz_version: selectedResourceInheritanceAAZVersionMap[resourceId],
                },
            }
            if (updateOption === UpdateOptions[1]) {
                // patch first
                const resource = resourceMap[resourceId];
                const operations = resource.versions.find(v => v.version === selectedVersion)?.operations;
                if (operations) {
                    for (const opName in operations) {
                        if (operations[opName].toLowerCase() === "patch") {
                            res.options.update_by = "PatchOnly"
                            break
                        }
                    }
                }
            } else if (updateOption === UpdateOptions[2]) {
                // No update command generation
                res.options.update_by = "None"
            }
            resources.push(res)
        });

        const requestBody = {
            module: selectedModule!.slice().replace(moduleOptionsCommonPrefix, ''),
            version: selectedVersion,
            resources: resources,
        }

        this.setState({
            invalidText: undefined,
            loading: true
        });

        axios.post(`/AAZ/Editor/Workspaces/${this.props.workspaceName}/CommandTree/Nodes/aaz/AddSwagger`, requestBody)
            .then(res => {
                this.setState({
                    loading: false
                });
                this.props.onClose(true);
            })
            .catch((err) => {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    this.setState({
                        invalidText: `ResponseError: ${data.message!}`,
                    })
                }
            });
    }

    onModuleSelectorUpdate = (moduleValueUrl: string | null) => {
        if (this.state.selectedModule !== moduleValueUrl) {
            this.loadResourceProviders(moduleValueUrl);
        }
        this.setState({
            selectedModule: moduleValueUrl
        });
    }

    onResourceProviderUpdate = (resourceProviderUrl: string | null) => {
        if (this.state.selectedResourceProvider !== resourceProviderUrl) {
            this.loadResources(resourceProviderUrl);
        }
        this.setState({
            selectedResourceProvider: resourceProviderUrl
        })
    }

    onVersionUpdate = (version: string | null) => {
        this.setState(preState => {
            let selectedResources = preState.selectedResources;
            let resourceOptions: Resource[] = [];
            let selectedResourceInheritanceAAZVersionMap = preState.selectedResourceInheritanceAAZVersionMap;
            if (version != null) {
                selectedResources = new Set();
                selectedResourceInheritanceAAZVersionMap = {};
                resourceOptions = [...preState.versionResourceIdMap[version]]
                    .sort((a, b) => a.id.localeCompare(b.id))
                    .filter(r => !preState.existingResources.has(r.id));
                resourceOptions.forEach((r) => {
                    if (preState.selectedResources.has(r.id)) {
                        selectedResources.add(r.id);
                        if (r.aazVersions && r.aazVersions.findIndex(v => v === version) >= 0) {
                            selectedResourceInheritanceAAZVersionMap[r.id] = version;
                        } else {
                            selectedResourceInheritanceAAZVersionMap[r.id] = preState.selectedResourceInheritanceAAZVersionMap[r.id];
                        }
                    }
                })
            }
            return {
                ...preState,
                resourceOptions: resourceOptions,
                selectedVersion: version,
                preferredAAZVersion: version,
                selectedResources: selectedResources,
                selectedResourceInheritanceAAZVersionMap: selectedResourceInheritanceAAZVersionMap,
            }
        })
    }

    onUpdateOptionUpdate = (updateOption: string | null) => {

        this.setState({
            updateOption: updateOption ?? UpdateOptions[0]
        })
    }

    onResourceItemClick = (resourceId: string) => {
        return () => {
            this.setState(preState => {
                const selectedResources = new Set(preState.selectedResources);
                let selectedResourceInheritanceAAZVersionMap = { ...preState.selectedResourceInheritanceAAZVersionMap };
                if (selectedResources.has(resourceId)) {
                    selectedResources.delete(resourceId);
                    delete selectedResourceInheritanceAAZVersionMap[resourceId];
                } else if (!preState.existingResources.has(resourceId)) {
                    selectedResources.add(resourceId);
                    const aazVersions = preState.resourceMap[resourceId].aazVersions;
                    let inheritanceAAZVersion = null;
                    if (aazVersions) {
                        if (aazVersions.findIndex(v => v === preState.preferredAAZVersion) >= 0) {
                            inheritanceAAZVersion = preState.preferredAAZVersion;
                        } else {
                            inheritanceAAZVersion = aazVersions[0];
                        }
                    }
                    selectedResourceInheritanceAAZVersionMap[resourceId] = inheritanceAAZVersion;
                }

                return {
                    ...preState,
                    selectedResources: selectedResources,
                    selectedResourceInheritanceAAZVersionMap: selectedResourceInheritanceAAZVersionMap,
                }
            })
        }
    }

    onSelectedAllClick = () => {
        this.setState(preState => {
            const selectedResources = new Set(preState.selectedResources);
            let selectedResourceInheritanceAAZVersionMap = { ...preState.selectedResourceInheritanceAAZVersionMap };
            if (selectedResources.size === preState.resourceOptions.length) {
                selectedResources.clear()
                selectedResourceInheritanceAAZVersionMap = {}
            } else {
                preState.resourceOptions.forEach((r) => {
                    selectedResources.add(r.id)
                    const aazVersions = preState.resourceMap[r.id].aazVersions;
                    let inheritanceAAZVersion = null;
                    if (aazVersions) {
                        if (aazVersions.findIndex(v => v === preState.preferredAAZVersion) >= 0) {
                            inheritanceAAZVersion = preState.preferredAAZVersion;
                        } else {
                            inheritanceAAZVersion = aazVersions[0];
                        }
                    }
                    selectedResourceInheritanceAAZVersionMap[r.id] = inheritanceAAZVersion;
                })
            }
            return {
                ...preState,
                selectedResources: selectedResources,
                selectedResourceInheritanceAAZVersionMap: selectedResourceInheritanceAAZVersionMap,
            }
        })
    }

    onResourceInheritanceAAZVersionUpdate = (resourceId: string, aazVersion: string | null) => {
        this.setState(preState => {
            let selectedResourceInheritanceAAZVersionMap = { ...preState.selectedResourceInheritanceAAZVersionMap };
            selectedResourceInheritanceAAZVersionMap[resourceId] = aazVersion;
            let preferredAAZVersion = preState.preferredAAZVersion;
            if (aazVersion !== null) {
                preferredAAZVersion = aazVersion;
            }

            return {
                ...preState,
                selectedResourceInheritanceAAZVersionMap: selectedResourceInheritanceAAZVersionMap,
                preferredAAZVersion: preferredAAZVersion,
            }
        })
    }

    render() {
        const { selectedResources, existingResources, resourceOptions, resourceMap, selectedVersion, selectedModule, selectedResourceInheritanceAAZVersionMap, filterText } = this.state;
        return (
            <React.Fragment>
                <AppBar sx={{ position: "fixed" }}>
                    <Toolbar>
                        <IconButton
                            edge="start"
                            color="inherit"
                            onClick={this.handleClose}
                            aria-label="close"
                        >
                            <CloseIcon />
                        </IconButton>
                        <Typography sx={{ ml: 2, flex: 1, flexDirection: "row", display: "flex", justifyContent: "center", alignContent: "center" }} variant='h5' component='div'>
                            Add Swagger Resources
                        </Typography>
                    </Toolbar>
                </AppBar>
                <EditorPageLayout
                >
                    <Box sx={{
                        flexShrink: 0,
                        width: 250,
                        flexDirection: 'column',
                        display: 'flex',
                        alignItems: 'stretch',
                        justifyContent: 'flex-start',
                        marginRight: '3vh'
                    }}>
                        <ListSubheader> Swagger Filters</ListSubheader>
                        <MiddlePadding />
                        <SwaggerItemSelector
                            name='Swagger Module'
                            commonPrefix={this.state.moduleOptionsCommonPrefix}
                            options={this.state.moduleOptions}
                            value={this.state.selectedModule}
                            onValueUpdate={this.onModuleSelectorUpdate} />
                        <MiddlePadding />
                        <SwaggerItemSelector
                            name='Resource Provider'
                            commonPrefix={this.state.resourceProviderOptionsCommonPrefix}
                            options={this.state.resourceProviderOptions}
                            value={this.state.selectedResourceProvider}
                            onValueUpdate={this.onResourceProviderUpdate}
                        />
                        <MiddlePadding />
                        <SwaggerItemSelector
                            name='API Version'
                            commonPrefix=''
                            options={this.state.versionOptions}
                            value={this.state.selectedVersion}
                            onValueUpdate={this.onVersionUpdate}
                        />
                        <MiddlePadding2 />
                        <SwaggerItemSelector
                            name='Update Command Mode'
                            commonPrefix=''
                            options={this.state.updateOptions}
                            value={this.state.updateOption}
                            onValueUpdate={this.onUpdateOptionUpdate}
                        />
                        <MiddlePadding2 />

                        <Button
                            variant="contained"
                            onClick={this.handleSubmit}
                            disabled={selectedModule === null || selectedVersion === null || selectedResources.size < 1}
                        >
                            Submit
                        </Button>
                    </Box>
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
                                <Typography component='h6'>Resource Url</Typography>
                                <TextField
                                    autoFocus
                                    margin="normal"
                                    id="filterText"
                                    value={filterText}
                                    onChange={(event: any) => {
                                        this.setState({
                                            filterText: event.target.value,
                                            })
                                    }}
                                    label="Resource Filter"
                                    type="text"
                                    variant='outlined'
                                />

                                <Paper sx={{
                                    display: 'flex',
                                    flexDirection: 'row',
                                    alignItems: 'center',
                                    mt: 1,
                                }} variant="outlined" square>

                                    <ListItemButton sx={{ maxWidth: 180 }} dense onClick={this.onSelectedAllClick} disabled={resourceOptions.length === 0}>
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
                                    {/* <SortIcon sx={{ ml: 2, mr: 2 }} />
                                    <InputBase
                                        sx={{ flex: 1 }}
                                        placeholder="Filter by keywords."
                                        inputProps={{ 'aria-label': 'Filter by keywords.' }}
                                    /> */}
                                </Paper>
                            </Box>
                        </ListSubheader>}
                    >

                        {resourceOptions.length > 0 && <Paper sx={{ ml: 2, mr: 2 }} variant="outlined" square>
                            {resourceOptions.filter((option) => {
                                if (filterText.trim().length > 0) {
                                    return option.id.indexOf(filterText.trim()) > -1;
                                }else{
                                    return option;
                                }
                            }).map((option) => {
                                const labelId = `resource-${option.id}`;
                                const selected = selectedResources.has(option.id);
                                const inheritanceOptions = resourceMap[option.id]?.aazVersions;
                                let selectedInheritance = null;
                                if (selectedResourceInheritanceAAZVersionMap !== null) {
                                    selectedInheritance = selectedResourceInheritanceAAZVersionMap[option.id];
                                }
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
                                                checked={selected || existingResources.has(option.id)}
                                                tabIndex={-1}
                                                disableRipple
                                                inputProps={{ 'aria-labelledby': labelId }}
                                            />
                                        </ListItemIcon>
                                        <ListItemText id={labelId}
                                            primary={option.id}
                                            primaryTypographyProps={{
                                                variant: "h6",
                                            }}
                                        />
                                    </ListItemButton>
                                    {selected && <FormControl sx={{ m: 1, minWidth: 120 }}>
                                        <InputLabel id={`${labelId}-inheritance-select-label`}>Inheritance</InputLabel>
                                        <Select
                                            id={`${labelId}-inheritance-select`}
                                            value={selectedInheritance === null ? "_NULL_" : selectedInheritance}
                                            onChange={(event) => {
                                                this.onResourceInheritanceAAZVersionUpdate(option.id, event.target.value === "_NULL_" ? null : event.target.value);
                                            }}
                                            size="small"
                                        >
                                            <MenuItem value="_NULL_" key={`${labelId}-inheritance-select-null`}>
                                                None
                                            </MenuItem>
                                            {inheritanceOptions && inheritanceOptions.map((inheritanceOption) => {
                                                return (<MenuItem value={inheritanceOption} key={`${labelId}-inheritance-select-${inheritanceOption}`}>
                                                    {inheritanceOption}
                                                </MenuItem>);
                                            })}
                                        </Select>
                                        <FormHelperText>Inherit modification from exported command models in aaz</FormHelperText>
                                    </FormControl>}
                                </ListItem>
                            })}
                        </Paper>}
                    </List>
                </EditorPageLayout>
                <Backdrop
                    sx={{ color: '#fff', zIndex: (theme: any) => theme.zIndex.drawer + 1 }}
                    open={this.state.loading}
                >
                    {this.state.invalidText !== undefined &&
                        <Alert sx={{
                            maxWidth: "80%",
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "stretch",
                            justifyContent: "flex-start",
                        }}
                            variant="filled"
                            severity='error'
                            onClose={() => {
                                this.setState({
                                    invalidText: undefined,
                                    loading: false,
                                })
                            }}
                        >
                            {this.state.invalidText}
                        </Alert>
                    }
                    {this.state.invalidText === undefined && <CircularProgress color='inherit' />}
                </Backdrop>
            </React.Fragment>
        )
    }
}



interface SwaggerItemsSelectorProps {
    commonPrefix: string,
    options: string[],
    name: string,
    value: string | null,
    onValueUpdate: (value: string | null) => void
}


class SwaggerItemSelector extends React.Component<SwaggerItemsSelectorProps> {

    constructor(props: SwaggerItemsSelectorProps) {
        super(props);
        this.state = {
            value: this.props.options.length === 1 ? this.props.options[0] : null,
        }
    }

    render() {
        // const { value } = this.state;
        const { name, options, commonPrefix, value } = this.props;
        return (
            <Autocomplete
                id={name}
                value={value}
                options={options}
                onChange={(event, newValue: any) => {
                    this.props.onValueUpdate(newValue);
                }}
                getOptionLabel={(option) => {
                    return option.replace(commonPrefix, '');
                }}
                renderOption={(props, option) => {
                    return (
                        <Box component='li'
                            {...props}
                        >
                            {option.replace(commonPrefix, '')}
                        </Box>
                    )
                }}
                selectOnFocus
                clearOnBlur
                renderInput={(params) => (
                    <TextField
                        {...params}
                        size='small'
                        // variant='filled'
                        label={name}
                        required
                    />
                )}
            />
        )
    }
}


// class WSEditorResourceListHeader extends React.Com


export default WSEditorSwaggerPicker;
