import { Autocomplete, createFilterOptions, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField, Typography } from '@mui/material';
import { Box } from '@mui/system';
import axios from 'axios';
import * as React from 'react';
import { Button } from 'reactstrap';


interface CLIModule {
    name: string
    folder: string | null
    url: string | null
}

interface CLIModuleSelectorProps {
    repo: string
    name: string
}

interface CLIModuleSelectorState {
    options: any[],
    value: CLIModule | null,
    openDialog: boolean,
    createDialogValue: CLIModule
}

interface InputType {
    inputValue: string,
    title: string,
}

const filter = createFilterOptions<CLIModule | InputType>();


class CLIModuleSelector extends React.Component<CLIModuleSelectorProps, CLIModuleSelectorState> {

    constructor(props: CLIModuleSelectorProps) {
        super(props);
        this.state = {
            options: [],
            value: null,
            openDialog: false,
            createDialogValue: {
                name: "",
                folder: null,
                url: null
            }
        }

    }

    componentDidMount() {
        this.loadModules();
    }

    loadModules = () => {
        axios.get("/CLI/Az/" + this.props.repo + "/Modules")
            .then((res) => {
                let options = res.data.map((option: any) => {
                    return {
                        name: option.name,
                        folder: option.folder,
                        url: option.url,
                    }
                })
                this.setState({
                    options: options
                })
            })
            .catch((err) => console.error(err.response));
    }

    handleDialogSubmit = (event: any) => {
        const form = event.currentTarget;
        if (form.checkValidity() === true) {
            const moduleName = this.state.createDialogValue.name;

            axios.post("/CLI/Az/" + this.props.repo + "/Modules", {
                name: moduleName,
            })
                .then((res) => {
                    let module = res.data;
                    let value = {
                        name: module.name,
                        folder: module.folder,
                        url: module.url,
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
                folder: null,
                url: null,
            },
            openDialog: false,
        })
    }

    onValueUpdated = (value: any) => {
        this.setState({
            value: value
        });
        if (value.url) {
            window.location.href = `/?#/Generation/${this.props.repo}/${value.name}`
        }
    }

    render() {
        const { options, value, openDialog, createDialogValue } = this.state

        const { repo, name } = this.props

        return (
            <React.Fragment>
                <Autocomplete
                    id={repo + "-module-select"}
                    value={value}
                    sx={{ width: 280 }}
                    options={options}
                    autoHighlight
                    onChange={(event, newValue: any) => {
                        if (typeof newValue === 'string') {
                            setTimeout(() => {
                                this.setState({
                                    openDialog: true,
                                    createDialogValue: {
                                        name: newValue,
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
                            {'Create module in Azure CLI' + repo === 'Extension' ? ' Extension' : ''}
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
                                label="Module Name"
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

export default CLIModuleSelector
