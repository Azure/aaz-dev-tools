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
    FormControl,
    TextField,
    InputAdornment,
    IconButton,
} from "@mui/material";
import { useParams } from "react-router";
import axios from "axios";
import CLIModGeneratorToolBar from "./CLIModGeneratorToolBar";
import CLIModGeneratorProfileCommandTree, { ExportModViewProfile, InitializeCommandTreeByModView, ProfileCommandTree } from "./CLIModGeneratorProfileCommandTree";
import CLIModGeneratorProfileTabs from "./CLIModGeneratorProfileTabs";
import { CLIModView, CLIModViewProfiles } from "./CLIModuleCommon";
import { FolderOpen } from "@mui/icons-material";

interface CLISpecsSimpleCommand {
    names: string[],
}

interface CLISpecsSimpleCommands {
    [name: string]: CLISpecsSimpleCommand,
}

interface CLISpecsSimpleCommandGroups {
    [name: string]: CLISpecsSimpleCommandGroup,
}

interface CLISpecsSimpleCommandGroup {
    names: string[],
    commands: CLISpecsSimpleCommands,
    commandGroups: CLISpecsSimpleCommandGroups,
}

interface CLISpecsSimpleCommandTree {
    root: CLISpecsSimpleCommandGroup,
}

interface CLISpecsHelp {
    short: string,
    lines?: string[],
}

interface CLISpecsResource {
    plane: string,
    id: string,
    version: string,
    subresource?: string,
}

interface CLISpecsCommandExample {
    name: string,
    commands: string[],
}

interface CLISpecsCommandVersion {
    name: string,
    stage?: string,
    resources: CLISpecsResource[],
    examples?: CLISpecsCommandExample[],
}

interface CLISpecsCommand {
    names: string[],
    help: CLISpecsHelp,
    versions: CLISpecsCommandVersion[],
}

interface CLISpecsCommandGroup {
    names: string[],
    help?: CLISpecsHelp,
    commands?: CLISpecsCommands,
    commandGroups?: CLISpecsCommandGroups,
}

interface CLISpecsCommandGroups {
    [name: string]: CLISpecsCommandGroup,
}

interface CLISpecsCommands {
    [name: string]: CLISpecsCommand,
}

async function retrieveCommand(names: string[]): Promise<CLISpecsCommand> {
    return axios.get(`/AAZ/Specs/CommandTree/Nodes/aaz/${names.slice(0, -1).join('/')}/Leaves/${names[names.length - 1]}`).then(res => res.data);
}

async function retrieveCommands(namesList: string[][]): Promise<CLISpecsCommand[]> {
    const namesListData = namesList.map(names => ['aaz', ...names]);
    return axios.post(`/AAZ/Specs/CommandTree/Nodes/Leaves`, namesListData).then(res => res.data);
}

const useSpecsCommandTree: () => (namesList: string[][]) => Promise<CLISpecsCommand[]> = () => {
    const commandCache = React.useRef(new Map<string, Promise<CLISpecsCommand>>());

    const fetchCommands = React.useCallback(async (namesList: string[][]) => {
        const promiseResults = [];
        const uncachedNamesList = [];
        for (const names of namesList) {
            const cachedPromise = commandCache.current.get(names.join('/'));
            if (!cachedPromise) {
                uncachedNamesList.push(names);
            } else {
                promiseResults.push(cachedPromise);
            }
        }
        if (uncachedNamesList.length === 0) {
            return await Promise.all(promiseResults);
        } else if (uncachedNamesList.length === 1) {
            const commandPromise = retrieveCommand(uncachedNamesList[0]);
            commandCache.current.set(uncachedNamesList[0].join('/'), commandPromise);
            return (await Promise.all(promiseResults.concat(commandPromise)));
        } else {
            const uncachedCommandsPromise = retrieveCommands(uncachedNamesList);
            uncachedNamesList.forEach((names, idx) => {
                commandCache.current.set(names.join('/'), uncachedCommandsPromise.then(commands => commands[idx]));
            });
            return (await Promise.all(promiseResults)).concat(await uncachedCommandsPromise);
        }
    }, [commandCache]);
    return fetchCommands;
}


interface ProfileCommandTrees {
    [name: string]: ProfileCommandTree,
}

interface CLIModuleGeneratorProps {
    params: {
        repoName: string;
        moduleName: string;
    };
}

const CLIModuleGenerator: React.FC<CLIModuleGeneratorProps> = ({ params }) => {
    const [loading, setLoading] = React.useState(false);
    const [invalidText, setInvalidText] = React.useState<string | undefined>(undefined);
    const [profiles, setProfiles] = React.useState<string[]>([]);
    const [commandTrees, setCommandTrees] = React.useState<ProfileCommandTrees>({});
    const [selectedProfile, setSelectedProfile] = React.useState<string | undefined>(undefined);
    const [showGenerateDialog, setShowGenerateDialog] = React.useState(false);
    const [showDraftPowerShellDialog, setShowDraftPowerShellDialog] = React.useState(false);

    const fetchCommands = useSpecsCommandTree();

    React.useEffect(() => {
        loadModule();
    }, []);

    const loadModule = async () => {
        try {
            setLoading(true);
            const profiles: string[] = await axios.get(`/CLI/Az/Profiles`).then(res => res.data);

            const modView: CLIModView = await axios.get(`/CLI/Az/${params.repoName}/Modules/${params.moduleName}`).then(res => res.data);

            const simpleTree: CLISpecsSimpleCommandTree = await axios.get(`/AAZ/Specs/CommandTree/Simple`).then(res => res.data);

            Object.keys(modView!.profiles).forEach((profile) => {
                const idx = profiles.findIndex(v => v === profile);
                if (idx === -1) {
                    throw new Error(`Invalid profile ${profile}`);
                }
            });

            const commandTrees = Object.fromEntries(profiles.map((profile) => {
                return [profile, InitializeCommandTreeByModView(profile, modView!.profiles[profile] ?? null, simpleTree)];
            }));

            const selectedProfile = profiles.length > 0 ? profiles[0] : undefined;
            setProfiles(profiles);
            setCommandTrees(commandTrees);
            setSelectedProfile(selectedProfile);
            setLoading(false);
        } catch (err: any) {
            console.error(err);
            if (err.response?.data?.message) {
                const data = err.response!.data!;
                setInvalidText(`ResponseError: ${data.message!}`);
            } else {
                setInvalidText(`Error: ${err}`);
            }
        }
    };

    const selectedCommandTree = selectedProfile ? commandTrees[selectedProfile] : undefined;

    const handleBackToHomepage = () => {
        window.open('/?#/cli', "_blank");
    };

    const handleGenerate = () => {
        setShowGenerateDialog(true);
    };

    const handleDraftPowerShell = () => {
        setShowDraftPowerShellDialog(true);
    };

    const handleGenerationClose = () => {
        setShowGenerateDialog(false);
    };

    const handleDraftPowerShellClose = () => {
        setShowDraftPowerShellDialog(false);
    };

    const onProfileChange = React.useCallback((selectedProfile: string) => {
        setSelectedProfile(selectedProfile);
    }, []);

    const onSelectedProfileTreeUpdate = React.useCallback((updater: ((oldTree: ProfileCommandTree) => ProfileCommandTree) | ProfileCommandTree) => {
        setCommandTrees((commandTrees) => {
            const selectedCommandTree = commandTrees[selectedProfile!];
            const newTree = typeof updater === 'function' ? updater(selectedCommandTree!) : updater;
            return { ...commandTrees, [selectedProfile!]: newTree }
        });
    }, [selectedProfile]);

    return (
        <React.Fragment>
            <CLIModGeneratorToolBar
                moduleName={params.moduleName}
                onHomePage={handleBackToHomepage}
                onGenerate={handleGenerate}
                onDraftPowerShell={handleDraftPowerShell}
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
                    {selectedProfile !== undefined && (
                        <CLIModGeneratorProfileTabs
                            value={selectedProfile}
                            profiles={profiles}
                            onChange={onProfileChange}
                        />
                    )}
                </Drawer>
                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        p: 2,
                    }}
                >
                    <Toolbar sx={{ flexShrink: 0 }} />
                    {selectedCommandTree !== undefined && (
                        <CLIModGeneratorProfileCommandTree
                            profile={selectedProfile}
                            profileCommandTree={selectedCommandTree}
                            onChange={onSelectedProfileTreeUpdate}
                            onLoadCommands={fetchCommands}
                        />
                    )}
                </Box>
            </Box>
            {showGenerateDialog && (
                <GenerateDialog
                    repoName={params.repoName}
                    moduleName={params.moduleName}
                    profileCommandTrees={commandTrees}
                    open={showGenerateDialog}
                    onClose={handleGenerationClose}
                />
            )}
            {!showGenerateDialog && showDraftPowerShellDialog && (
                <DraftPowerShellDialog
                    open={showDraftPowerShellDialog}
                    onClose={handleDraftPowerShellClose}
                />
            )}
            <Backdrop
                sx={{ color: '#fff', zIndex: (theme: any) => theme.zIndex.drawer + 1 }}
                open={loading}
            >
                {invalidText !== undefined ? (
                    <Alert
                        sx={{
                            maxWidth: "80%",
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "stretch",
                            justifyContent: "flex-start",
                            whiteSpace: "pre-line",
                        }}
                        variant="filled"
                        severity='error'
                        onClose={() => {
                            setInvalidText(undefined);
                            setLoading(false);
                        }}
                    >
                        {invalidText}
                    </Alert>
                ) : (
                    <CircularProgress color='inherit' />
                )}
            </Backdrop>
        </React.Fragment>
    );
};

function GenerateDialog(props: {
    repoName: string;
    moduleName: string;
    profileCommandTrees: ProfileCommandTrees;
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
        Object.values(props.profileCommandTrees).forEach(tree => {
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
                console.error(err);
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
        Object.values(props.profileCommandTrees).forEach(tree => {
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
                console.error(err);
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

function DraftPowerShellDialog(props: {
    open: boolean;
    onClose: (generated: boolean) => void;
}) {

    const [loading, setLoading] = React.useState<boolean>(false);
    const [updating, setUpdating] = React.useState<boolean>(false);
    const [invalidText, setInvalidText] = React.useState<string | undefined>(
        undefined
    );
    const [powershellPath, setPowershellPath] = React.useState<string | undefined>(undefined);

    const handleClose = () => {
        props.onClose(false);
    };

    const handleDraftPowerShell = () => {
        setUpdating(true);
        // axios
        //     .post(`/CLI/Az/${props.repoName}/Modules/${props.moduleName}/DraftPowerShell`)
        //     .then(() => {
        //         setUpdating(false);
        //         props.onClose(true);
        //     })
    }

    React.useEffect(() => {
        if (props.open) {
            setLoading(true);
            // call /PS/PowerShell/Path api to get the path of the PowerShell script
            axios.get(`/PS/Powershell/Path`).then(res => {
                setPowershellPath(res.data.path || undefined);
                setLoading(false);
            }).catch(err => {
                console.error(err);
                setLoading(false);
            });
        } else {
            setLoading(false);
        }
    }, [props.open]);

    return <Dialog disableEscapeKeyDown open={props.open} maxWidth="md" fullWidth>
        <DialogTitle>Draft PowerShell Generation from CLI</DialogTitle>
        <DialogContent>
            {invalidText && <Alert variant="filled" severity="error"> {invalidText} </Alert>}
            {loading && <CircularProgress />}
            {!loading && <FormControl fullWidth sx={{ mt: 2 }}>
                <TextField
                    label="PowerShell Path"
                    value={powershellPath || ''}
                    onChange={(e) => setPowershellPath(e.target.value)}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton
                                    onClick={async () => {
                                        const dirHandler = await (window as any).showDirectoryPicker();
                                        const path = await dirHandler.resolve();
                                        setPowershellPath(path);
                                    }}
                                >
                                    <FolderOpen />
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />
            </FormControl>}
        </DialogContent>
        <DialogActions>
                {updating &&
                    <Box sx={{ width: "100%" }}>
                        <LinearProgress color="secondary" />
                    </Box>
                }
                {!updating && <React.Fragment>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleDraftPowerShell}>Draft</Button>
                </React.Fragment>}
            </DialogActions>
    </Dialog>
}

const CLIModuleGeneratorWrapper = (props: any) => {
    const params = useParams();
    return <CLIModuleGenerator params={params} {...props} />
}

export type { CLISpecsCommandGroup, CLISpecsCommand, CLISpecsSimpleCommandTree, CLISpecsSimpleCommandGroup, CLISpecsSimpleCommand };
export { CLIModuleGeneratorWrapper as CLIModuleGenerator };
