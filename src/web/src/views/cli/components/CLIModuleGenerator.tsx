import { useState, useEffect, useCallback, Fragment, FC } from "react";
import { Backdrop, Box, CircularProgress, Drawer, Toolbar, Alert } from "@mui/material";
import { useParams } from "react-router";
import { cliApi, errorHandlerApi } from "../../../services";
import CLIModGeneratorToolBar from "./CLIModGeneratorToolBar";
import CLIModGeneratorProfileCommandTree from "./CLIModGeneratorProfileCommandTree";
import { initializeCommandTreeByModView, ProfileCommandTree } from "../utils/commandTreeInitialization";
import CLIModGeneratorProfileTabs from "./CLIModGeneratorProfileTabs";
import { CLIModView } from "../interfaces";
import GenerateDialog, { type ProfileCommandTrees } from "./GenerateDialog";
import { useSpecsCommandTree } from "../hooks";

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

interface CLIModuleGeneratorProps {
  params: {
    repoName: string;
    moduleName: string;
  };
}

const CLIModuleGenerator: FC<CLIModuleGeneratorProps> = ({ params }) => {
  const [loading, setLoading] = useState(false);
  const [invalidText, setInvalidText] = useState<string | undefined>(undefined);
  const [profiles, setProfiles] = useState<string[]>([]);
  const [commandTrees, setCommandTrees] = useState<ProfileCommandTrees>({});
  const [selectedProfile, setSelectedProfile] = useState<string | undefined>(undefined);
  const [showGenerateDialog, setShowGenerateDialog] = useState(false);

  const fetchCommands = useSpecsCommandTree();

  useEffect(() => {
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
          return [profile, initializeCommandTreeByModView(profile, modView!.profiles[profile] ?? null, simpleTree)];
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

  const onProfileChange = useCallback((selectedProfile: string) => {
    setSelectedProfile(selectedProfile);
  }, []);

  const onSelectedProfileTreeUpdate = useCallback(
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
    <Fragment>
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
    </Fragment>
  );
};

const CLIModuleGeneratorWrapper = (props: any) => {
  const params = useParams();
  return <CLIModuleGenerator params={params} {...props} />;
};

export type { CLISpecsCommand } from "../hooks";
export type { CLISpecsSimpleCommandTree, CLISpecsSimpleCommandGroup, CLISpecsSimpleCommand };
export { CLIModuleGeneratorWrapper as CLIModuleGenerator };
