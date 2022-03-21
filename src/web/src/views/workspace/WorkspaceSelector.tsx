import { Autocomplete, createFilterOptions, Dialog, DialogActions, DialogContent, DialogTitle, TextField } from '@mui/material';
import { Box } from '@mui/system';
import axios from 'axios';
import * as React from 'react';
import { Button } from 'reactstrap';
import { Url } from 'url';


interface Workspace {
    name: string,
    plane: string | null,
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
    createDialogValue: Workspace
    // dialogValidated: boolean
}

interface InputType {
    inputValue: string,
    title: string,
}

const filter = createFilterOptions<Workspace | InputType>();

const defaultPlane = "mgmt-plane"

class WorkspaceSelector extends React.Component<WorkspaceSelectorProps, WorkspaceSelectorState> {

    constructor(props: WorkspaceSelectorProps) {
        super(props);
        this.state = {
            options: [],
            value: null,
            openDialog: false,
            createDialogValue: {
                name: "",
                plane: null,
                lastModified: null,
                url: null,
                folder: null,
            },
            // dialogValidated: false
        }
    }

    componentDidMount() {
        this.loadWorkspaces();
    }

    loadWorkspaces = () => {
        axios.get("/AAZ/Editor/Workspaces")
            .then((res) => {
                let options = res.data.map((option: any) => {
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
            })
            .catch((err) => console.error(err));
    }

    handleDialogSubmit = (event: any) => {
        const form = event.currentTarget;
        if (form.checkValidity() === true) {
            const workspaceName = this.state.createDialogValue.name
            const plane = this.state.createDialogValue.plane
            axios.post('/AAZ/Editor/Workspaces', {
                name: workspaceName,
                plane: plane,
            })
                .then((res) => {
                    let workspace = res.data;
                    let value = {
                        name: workspace.name,
                        lastModified: new Date(workspace.updated * 1000),
                        url: workspace.url,
                        plane: workspace.plane,
                        folder: workspace.folder
                    }
                    setTimeout(() => {
                        this.onValueUpdated(value);
                    })
                    this.handleDialogClose();
                })
                .catch(error => {
                    console.error(error.response);
                })
        }
    }

    handleDialogClose = () => {
        this.setState({
            createDialogValue: {
                name: "",
                plane: null,
                lastModified: null,
                url: null,
                folder: null,
            },
            openDialog: false,
            // dialogValidated: false,
        })
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
        const { options, value, openDialog, createDialogValue } = this.state
        const { name } = this.props
        return (
            <React.Fragment>
                <Autocomplete
                    id="workspace-select"
                    value={value}
                    sx={{ width: 280 }}
                    options={options}
                    autoHighlight
                    onChange={(event, newValue: any) => {
                        if (typeof newValue === 'string') {
                            // timeout to avoid instant validation of the dialog's form.
                            setTimeout(() => {
                                this.setState({
                                    openDialog: true,
                                    createDialogValue: {
                                        name: newValue,
                                        plane: defaultPlane,
                                        lastModified: null,
                                        url: null,
                                        folder: null,
                                    }
                                })
                            });
                        } else if (newValue && newValue.inputValue) {
                            this.setState({
                                openDialog: true,
                                createDialogValue: {
                                    name: newValue.inputValue,
                                    plane: defaultPlane,
                                    lastModified: null,
                                    url: null,
                                    folder: null,
                                }
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
                        let labelName = (option && option.title) ? option.title : option.name;
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
                <Dialog open={openDialog} onClose={this.handleDialogClose}>
                    <Box component='form' onSubmit={this.handleDialogSubmit}>
                        <DialogTitle>
                            Create a new workspace
                        </DialogTitle>
                        <DialogContent>
                            <TextField
                                autoFocus
                                margin="normal"
                                id="name"
                                required
                                value={createDialogValue.name}
                                onChange={(event: any) => {
                                    this.setState({
                                        createDialogValue: {
                                            ...createDialogValue,
                                            name: event.target.value,
                                        }
                                    })
                                }}
                                label="Name"
                                type="text"
                                variant='standard'
                            />
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={this.handleDialogClose}>Cancel</Button>
                            <Button type="submit" color="success">Create</Button>
                        </DialogActions>
                    </Box>
                </Dialog>
            </React.Fragment>
        )
    }
}

export default WorkspaceSelector
