import * as React from "react";
import {
    Backdrop,
    Box,
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Drawer,
    LinearProgress,
    Toolbar,
    Alert,
} from "@mui/material";
import { useParams } from "react-router";
import axios from "axios";
import CLIModGeneratorToolBar from "./CLIModGeneratorToolBar";
import CLIModGeneratorProfileCommandTree, { BuildProfileCommandTree, ExportModViewProfile, ProfileCommandTree, UpdateProfileCommandTreeByModView } from "./CLIModGeneratorProfileCommandTree";
import CLIModGeneratorProfileTabs from "./CLIModGeneratorProfileTabs";
import { CLIModView, CLIModViewProfiles } from "./CLIModuleCommon";



interface CLIModuleGeneratorProps {
    params: {
        repoName: string;
        moduleName: string;
    };
}

interface CLIModuleGeneratorState {
    loading: boolean;
    invalidText?: string,
    profiles: string[];
    commandTrees: ProfileCommandTree[];
    selectedProfileIdx?: number;
    selectedCommandTree?: ProfileCommandTree;
    showGenerateDialog: boolean;
}


class CLIModuleGenerator extends React.Component<CLIModuleGeneratorProps, CLIModuleGeneratorState> {

    constructor(props: CLIModuleGeneratorProps) {
        super(props);
        this.state = {
            loading: false,
            invalidText: undefined,
            profiles: [],
            commandTrees: [],
            selectedProfileIdx: undefined,
            selectedCommandTree: undefined,
            showGenerateDialog: false,
        }
    }

    componentDidMount() {
        this.loadModule();
    }

    loadModule = async () => {
        try {
            this.setState({
                loading: true,
            });
            let res = await axios.get(`/CLI/Az/Profiles`);
            const profiles: string[] = res.data;

            res = await axios.get(`/AAZ/Specs/CommandTree/Nodes/aaz`);
            const commandTrees: ProfileCommandTree[] = profiles.map((profileName) => BuildProfileCommandTree(profileName, res.data));

            res = await axios.get(`/CLI/Az/${this.props.params.repoName}/Modules/${this.props.params.moduleName}`);
            const modView: CLIModView = res.data

            Object.keys(modView.profiles).forEach((profile) => {
                const idx = profiles.findIndex(v => v === profile);
                if (idx === -1) {
                    throw new Error(`Invalid profile ${profile}`);
                }
                commandTrees[idx] = UpdateProfileCommandTreeByModView(commandTrees[idx], modView.profiles[profile]);
            })

            const selectedProfileIdx = profiles.length > 0 ? 0 : undefined;
            const selectedCommandTree = selectedProfileIdx !== undefined ? commandTrees[selectedProfileIdx] : undefined;
            this.setState({
                loading: false,
                profiles: profiles,
                commandTrees: commandTrees,
                selectedProfileIdx: selectedProfileIdx,
                selectedCommandTree: selectedCommandTree
            })
        } catch (err: any) {
            console.error(err);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                this.setState({
                    invalidText: `ResponseError: ${data.message!}`,
                })
            } else {
                this.setState({
                    invalidText: `Error: ${err}`,
                })
            }
        }
    }

    handleBackToHomepage = () => {
        window.open('/?#/cli', "_blank");
    }

    handleGenerate = () => {
        this.setState({
            showGenerateDialog: true
        })
    }

    handleGenerationClose = () => {
        this.setState({
            showGenerateDialog: false
        })
    }

    onProfileChange = (selectedIdx: number) => {
        this.setState(preState => {
            return {
                ...preState,
                selectedProfileIdx: selectedIdx,
                selectedCommandTree: preState.commandTrees[selectedIdx],
            }
        })
    }

    onSelectedProfileTreeUpdate = (newTree: ProfileCommandTree) => {
        this.setState(preState => {
            return {
                ...preState,
                selectedCommandTree: newTree,
                commandTrees: preState.commandTrees.map((value, idx) => {return idx === preState.selectedProfileIdx ? newTree : value}),
            }
        })
    }

    render() {
        const { showGenerateDialog, selectedProfileIdx, selectedCommandTree, profiles, commandTrees } = this.state;
        return (
            <React.Fragment>
                <CLIModGeneratorToolBar
                    moduleName={this.props.params.moduleName}
                    onHomePage={this.handleBackToHomepage}
                    onGenerate={this.handleGenerate}
                />
                <Box sx={{ display: "flex" }}>
                    <Drawer
                        variant="permanent"
                        sx={{
                            width: 300,
                            flexShrink: 0,
                            [`& .MuiDrawer-paper`]: { width: 300, boxSizing: "border-box" },
                        }}
                    >
                        <Toolbar />
                        {selectedProfileIdx !== undefined && <CLIModGeneratorProfileTabs
                            value={selectedProfileIdx} profiles={profiles} onChange={this.onProfileChange} />}
                    </Drawer>
                    <Box
                        component="main"
                        sx={{
                            flexGrow: 1,
                            p: 2,
                        }}
                    >
                        <Toolbar sx={{ flexShrink: 0 }} />
                        {selectedCommandTree !== undefined && <CLIModGeneratorProfileCommandTree
                            profileCommandTree={selectedCommandTree} onChange={this.onSelectedProfileTreeUpdate}/>}
                    </Box>
                </Box>
                {showGenerateDialog && <GenerateDialog
                    repoName={this.props.params.repoName}
                    moduleName={this.props.params.moduleName}
                    profileCommandTrees={commandTrees}
                    open={showGenerateDialog}
                    onClose={this.handleGenerationClose}
                />}
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
        );
    }

}

function GenerateDialog(props: {
    repoName: string;
    moduleName: string;
    profileCommandTrees: ProfileCommandTree[];
    open: boolean;
    onClose: (generated: boolean) => void;
}) {
    const [updating, setUpdating] = React.useState<boolean>(false);
    const [invalidText, setInvalidText] = React.useState<string | undefined>(
        undefined
    );

    const handleClose = () => {
        props.onClose(false);
    };

    const handleGenerateAll = () => {
        const profiles: CLIModViewProfiles = {};
        props.profileCommandTrees.forEach(tree => {
            profiles[tree.name] = ExportModViewProfile(tree);
        })
        const data = {
            name: props.moduleName,
            profiles: profiles,
        }

        setUpdating(true);
        axios
            .put(
                `/CLI/Az/${props.repoName}/Modules/${props.moduleName}`,
                data
            )
            .then(() => {
                setUpdating(false);
                props.onClose(true);
            })
            .catch((err) => {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    setInvalidText(
                        `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                    );
                }
                setUpdating(false);
            });
    };

    const handleGenerateModified = () => {
        const profiles: CLIModViewProfiles = {};
        props.profileCommandTrees.forEach(tree => {
            profiles[tree.name] = ExportModViewProfile(tree);
        })
        const data = {
            name: props.moduleName,
            profiles: profiles,
        }

        setUpdating(true);
        axios
            .patch(
                `/CLI/Az/${props.repoName}/Modules/${props.moduleName}`,
                data
            )
            .then(() => {
                setUpdating(false);
                props.onClose(true);
            })
            .catch((err) => {
                console.error(err.response);
                if (err.response?.data?.message) {
                    const data = err.response!.data!;
                    setInvalidText(
                        `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
                    );
                }
                setUpdating(false);
            });
    }


    return (
        <Dialog disableEscapeKeyDown open={props.open}>
            <DialogTitle>Generate CLI commands to {props.moduleName}</DialogTitle>
            <DialogContent>
                {invalidText && <Alert variant="filled" severity="error"> {invalidText} </Alert>}
            </DialogContent>
            <DialogActions>
                {updating &&
                    <Box sx={{ width: "100%" }}>
                        <LinearProgress color="secondary" />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleGenerateAll}>Generate All</Button>
                    <Button onClick={handleGenerateModified}>Generate Edited Only</Button>
                </React.Fragment>}
            </DialogActions>
        </Dialog>
    );
}

const CLIModuleGeneratorWrapper = (props: any) => {
    const params = useParams();
    return <CLIModuleGenerator params={params} {...props} />
}

export { CLIModuleGeneratorWrapper as CLIModuleGenerator };
