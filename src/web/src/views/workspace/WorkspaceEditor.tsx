import * as React from 'react';
import { Typography, Box, Dialog, Slide } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useParams } from 'react-router';
import axios from 'axios';
import { TransitionProps } from '@mui/material/transitions';
import SwaggerResourcePicker from './SwaggerResourcePicker';
import EditorToolBar from '../../components/EditorToolBar';
import PageLayout from '../../components/PageLayout';

const TopPadding = styled(Box)(({ theme }) => ({
    [theme.breakpoints.up('sm')]: {
        height: '12vh',
    },
}));

const MiddlePadding = styled(Box)(({ theme }) => ({
    height: '6vh'
}));


type HelpType = {
    short: string,
    lines?: string[]
}

type Argument = {
    options: string[],
    type: string,
    help?: { short: string },
    required?: boolean,
    idPart?: string,
    args?: Argument[]
}

type ArgGroups = {
    args: Argument[],
    name: string
}[]

type ExampleType = {
    name: string,
    commands: string[]
}

type CommandResource = {
    id: string,
    version: string,
    swagger: string,
}

type Command = {
    help: HelpType,
    names: string[],
    resources: CommandResource[],
    version: string
}

type Commands = {
    [name: string]: Command
}

type CommandGroup = {
    commandGroups?: CommandGroups,
    commands?: Commands,
    names: string[],
    help?: HelpType,
    examples?: ExampleType[],
    argGroups?: ArgGroups
}

type CommandGroups = {
    [name: string]: CommandGroup
}

type CommandTree = {
    names: string[],
    commandGroups: CommandGroups
}

// type NumberToString = {
//     [index: number]: string
// }

// type StringToNumber = {
//     [name: string]: number
// }

// type NumberToTreeNode = {
//     [index: number]: TreeNode
// }

// type NumberToCommandGroup = {
//     [index: number]: CommandGroup
// }

// type TreeNode = {
//     id: number,
//     parent: number,
//     droppable: boolean,
//     text: string,
//     data: {
//         hasChildren: boolean,
//         type: string
//     }
// }

// type TreeDataType = TreeNode[]


interface WorkspaceEditorProps {
    params: {
        workspaceName: string
    }
}

interface WorkspaceEditorState {
    name: string
    plane: string,
    commandTree: CommandTree | null,
    showSwaggerResourcePicker: boolean
}

const swaggerResourcePickerTransition = React.forwardRef(function swaggerResourcePickerTransition(
    props: TransitionProps & { children: React.ReactElement },
    ref: React.Ref<unknown>
) {
    return <Slide direction='up' ref={ref} {...props} />

});

class WorkspaceEditor extends React.Component<WorkspaceEditorProps, WorkspaceEditorState> {

    constructor(props: WorkspaceEditorProps) {
        super(props);
        this.state = {
            name: this.props.params.workspaceName,
            plane: "",
            commandTree: null,
            showSwaggerResourcePicker: false,
        }
    }

    componentDidMount() {
        this.loadWorkspace();
    }

    loadWorkspace = () => {
        axios.get(`/AAZ/Editor/Workspaces/${this.props.params.workspaceName}`)
            .then(res => {
                let commandTree: CommandTree = res.data.commandTree;
                this.setState({
                    plane: res.data.plane,
                    commandTree: commandTree
                })
                if (!commandTree.commandGroups) {
                    this.showSwaggerResourcePicker();
                    return
                }
            })
            .catch((err) => console.log(err));
    }

    showSwaggerResourcePicker = () => {
        this.setState({ showSwaggerResourcePicker: true })
    }

    handleSwaggerResourcePickerClose = () => {
        this.setState({
            showSwaggerResourcePicker: false
        })
    }

    render() {
        const { showSwaggerResourcePicker, plane, commandTree, name } = this.state;

        return (
            <React.Fragment>
                <EditorToolBar>
                {/* <Button onClick={this.showSwaggerResourcePicker}>Add Swagger Resource</Button> */}
                </EditorToolBar>
                <PageLayout>
                    <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        flexDirection: 'column',
                    }}>
                        <TopPadding />
                        <Typography variant='h2' gutterBottom>
                            Welcome to
                        </Typography>
                        <Typography variant='h2' gutterBottom>
                            WorkspaceEditor
                        </Typography>
                        <MiddlePadding />
                    </Box>
                </PageLayout>

                <Dialog
                    fullScreen
                    open={showSwaggerResourcePicker}
                    onClose={this.handleSwaggerResourcePickerClose}
                    TransitionComponent={swaggerResourcePickerTransition}
                >
                    <SwaggerResourcePicker plane={plane} workspaceName={name} onClose={this.handleSwaggerResourcePickerClose} />
                </Dialog>

            </React.Fragment>

        )
    }
}

const WorkspaceEditorWrapper = (props: any) => {
    const params = useParams()

    return <WorkspaceEditor params={params} {...props} />
}

export { WorkspaceEditorWrapper as WorkspaceEditor };

export type { CommandTree, CommandResource };
