import * as React from 'react';
import { Typography, Box, Link, AppBar, Toolbar, IconButton, Button, Container } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloseIcon from '@mui/icons-material/Close';
import { CommandTree, CommandResource } from './WorkspaceEditor';
import axios from 'axios';
import PageLayout from '../../components/PageLayout';


interface SwaggerResourcePickerProps {
    workspaceName: string,
    plane: string,
    onClose: any
}

interface SwaggerResourcePickerState {
    plane: string
    commandTreeResources: CommandResource[]
    selectedModule: string,
    selectedResourceProvider: string,
    selectedVersion: string,
}



class SwaggerResourcePicker extends React.Component<SwaggerResourcePickerProps, SwaggerResourcePickerState> {

    constructor(props: SwaggerResourcePickerProps) {
        super(props);

        this.state = {
            plane: this.props.plane,
            commandTreeResources: [],
            selectedModule: "",
            selectedResourceProvider: "",
            selectedVersion: ""
        }
    }

    componentDidMount() {
        this.loadSwagger();
    }

    handleClose = () => {
        this.props.onClose()
    }

    handleSubmit = () => {
        this.props.onClose()
    }

    loadSwagger = () => {
        console.log(this.state)
    }

    loadModules = () => {
        const { plane } = this.state
        return axios.get(`/Swagger/Specs/${plane}`)

    }

    loadWorkspaceResources = () => {
        axios.get(`/AAZ/Editor/Workspaces/${this.props.workspaceName}/CommandTree/Nodes/aaz/Resources`)
            .then(res => {
                if (res.data && Array.isArray(res.data) && res.data.length > 0) {

                }
            })
            .catch((err) => console.log(err));
    }

    render() {
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
                        <Button color='success' onClick={this.handleSubmit}>
                            Submit
                        </Button>
                    </Toolbar>
                </AppBar>
                <PageLayout>
                    <Container sx={{
                        display: 'flex',
                        flexDirection: 'row',
                        alignItems: 'flex-start',
                        justifyContent: 'center'
                    }}>
                        <Button>plane</Button>
                        <Button>module</Button>
                        <Button>create</Button>

                    </Container>

                </PageLayout>
            </React.Fragment>
        )
    }
}

export default SwaggerResourcePicker;
