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
import { cliApi, errorHandlerApi } from "../../services";
import CLIModGeneratorToolBar from "./CLIModGeneratorToolBar";
import CLIModGeneratorProfileCommandTree, {
  ExportModViewProfile,
  InitializeCommandTreeByModView,
  ProfileCommandTree,
} from "./CLIModGeneratorProfileCommandTree";
import CLIModGeneratorProfileTabs from "./CLIModGeneratorProfileTabs";
import { CLIModView, CLIModViewProfiles } from "./interfaces";

interface CLISpecsSimpleCommand {
  names: string[];
}

interface CLISpecsSimpleCommands {
  [name: string]: CLISpecsSimpleCommand;
}

interface CLISpecsSimpleCommandGroups {
  [name: string]: CLISpecsSimpleCommandGroup;
}

interface CLISpecsSimpleCommandGroup {
  names: string[];
  commands: CLISpecsSimpleCommands;
  commandGroups: CLISpecsSimpleCommandGroups;
}

interface CLISpecsSimpleCommandTree {
  root: CLISpecsSimpleCommandGroup;
}

interface CLISpecsHelp {
  short: string;
  lines?: string[];
}

interface CLISpecsResource {
  plane: string;
  id: string;
  version: string;
  subresource?: string;
}

interface CLISpecsCommandExample {
  name: string;
  commands: string[];
}

interface CLISpecsCommandVersion {
  name: string;
  stage?: string;
  resources: CLISpecsResource[];
  examples?: CLISpecsCommandExample[];
}

interface CLISpecsCommand {
  names: string[];
  help: CLISpecsHelp;
  versions: CLISpecsCommandVersion[];
}

interface CLISpecsCommandGroup {
  names: string[];
  help?: CLISpecsHelp;
  commands?: CLISpecsCommands;
  commandGroups?: CLISpecsCommandGroups;
}

interface CLISpecsCommandGroups {
  [name: string]: CLISpecsCommandGroup;
}

interface CLISpecsCommands {
  [name: string]: CLISpecsCommand;
}

async function retrieveCommand(names: string[]): Promise<CLISpecsCommand> {
  return await cliApi.getSpecsCommand(names);
}

async function retrieveCommands(namesList: string[][]): Promise<CLISpecsCommand[]> {
  return await cliApi.retrieveCommands(namesList);
}

const useSpecsCommandTree: () => (namesList: string[][]) => Promise<CLISpecsCommand[]> = () => {
  const commandCache = React.useRef(new Map<string, Promise<CLISpecsCommand>>());

  const fetchCommands = React.useCallback(
    async (namesList: string[][]) => {
      const promiseResults = [];
      const uncachedNamesList = [];
      for (const names of namesList) {
        const cachedPromise = commandCache.current.get(names.join("/"));
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
        commandCache.current.set(uncachedNamesList[0].join("/"), commandPromise);
        return await Promise.all(promiseResults.concat(commandPromise));
      } else {
        const uncachedCommandsPromise = retrieveCommands(uncachedNamesList);
        uncachedNamesList.forEach((names, idx) => {
          commandCache.current.set(
            names.join("/"),
            uncachedCommandsPromise.then((commands) => commands[idx]),
          );
        });
        return (await Promise.all(promiseResults)).concat(await uncachedCommandsPromise);
      }
    },
    [commandCache],
  );
  return fetchCommands;
};

interface ProfileCommandTrees {
  [name: string]: ProfileCommandTree;
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

  const fetchCommands = useSpecsCommandTree();

  React.useEffect(() => {
    loadModule();
  }, []);

  const loadModule = async () => {
    try {
      setLoading(true);
      setInvalidText(undefined);
      const profiles = await cliApi.getCliProfiles();
      const modView: CLIModView = await cliApi.getCliModule(params.repoName, params.moduleName);
      const simpleTree: CLISpecsSimpleCommandTree = await cliApi.getSimpleCommandTree();

      Object.keys(modView!.profiles).forEach((profile) => {
        const idx = profiles.findIndex((v) => v === profile);
        if (idx === -1) {
          throw new Error(`Invalid profile ${profile}`);
        }
      });

      const commandTrees = Object.fromEntries(
        profiles.map((profile) => {
          return [profile, InitializeCommandTreeByModView(profile, modView!.profiles[profile] ?? null, simpleTree)];
        }),
      );

      const selectedProfile = profiles.length > 0 ? profiles[0] : undefined;
      setProfiles(profiles);
      setCommandTrees(commandTrees);
      setSelectedProfile(selectedProfile);
      setLoading(false);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
    }
  };

  const selectedCommandTree = selectedProfile ? commandTrees[selectedProfile] : undefined;

  const handleBackToHomepage = () => {
    window.open("/?#/cli", "_blank");
  };

  const handleGenerate = () => {
    setShowGenerateDialog(true);
  };

  const handleGenerationClose = () => {
    setShowGenerateDialog(false);
  };

  const onProfileChange = React.useCallback((selectedProfile: string) => {
    setSelectedProfile(selectedProfile);
  }, []);

  const onSelectedProfileTreeUpdate = React.useCallback(
    (updater: ((oldTree: ProfileCommandTree) => ProfileCommandTree) | ProfileCommandTree) => {
      setCommandTrees((commandTrees) => {
        const selectedCommandTree = commandTrees[selectedProfile!];
        const newTree = typeof updater === "function" ? updater(selectedCommandTree!) : updater;
        return { ...commandTrees, [selectedProfile!]: newTree };
      });
    },
    [selectedProfile],
  );

  return (
    <React.Fragment>
      <CLIModGeneratorToolBar
        moduleName={params.moduleName}
        onHomePage={handleBackToHomepage}
        onGenerate={handleGenerate}
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
            <CLIModGeneratorProfileTabs value={selectedProfile} profiles={profiles} onChange={onProfileChange} />
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
      <Backdrop sx={{ color: "#fff", zIndex: (theme: any) => theme.zIndex.drawer + 1 }} open={loading}>
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
            severity="error"
            onClose={() => {
              setInvalidText(undefined);
              setLoading(false);
            }}
          >
            {invalidText}
          </Alert>
        ) : (
          <CircularProgress color="inherit" />
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
  const [invalidText, setInvalidText] = React.useState<string | undefined>(undefined);

  const handleClose = () => {
    props.onClose(false);
  };

  const handleGenerateAll = async () => {
    const profiles: CLIModViewProfiles = {};
    Object.values(props.profileCommandTrees).forEach((tree) => {
      profiles[tree.name] = ExportModViewProfile(tree);
    });
    const data = {
      name: props.moduleName,
      profiles: profiles,
    };

    setUpdating(true);
    try {
      await cliApi.updateCliModule(props.repoName, props.moduleName, data);
      setUpdating(false);
      props.onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  const handleGenerateModified = async () => {
    const profiles: CLIModViewProfiles = {};
    Object.values(props.profileCommandTrees).forEach((tree) => {
      profiles[tree.name] = ExportModViewProfile(tree);
    });
    const data = {
      name: props.moduleName,
      profiles: profiles,
    };

    setUpdating(true);
    try {
      await cliApi.patchCliModule(props.repoName, props.moduleName, data);
      setUpdating(false);
      props.onClose(true);
    } catch (err: any) {
      console.error(err);
      setInvalidText(errorHandlerApi.getErrorMessage(err));
      setUpdating(false);
    }
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>Generate CLI commands to {props.moduleName}</DialogTitle>
      <DialogContent>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        {updating && (
          <Box sx={{ width: "100%" }}>
            <LinearProgress color="secondary" />
          </Box>
        )}
        {!updating && (
          <React.Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleGenerateAll}>Generate All</Button>
            <Button onClick={handleGenerateModified}>Generate Edited Only</Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
}

const CLIModuleGeneratorWrapper = (props: any) => {
  const params = useParams();
  return <CLIModuleGenerator params={params} {...props} />;
};

export type {
  CLISpecsCommandGroup,
  CLISpecsCommand,
  CLISpecsSimpleCommandTree,
  CLISpecsSimpleCommandGroup,
  CLISpecsSimpleCommand,
};
export { CLIModuleGeneratorWrapper as CLIModuleGenerator };
