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
  Autocomplete,
  createFilterOptions,
  Checkbox,
  FormControlLabel,
  FormLabel,
  FormGroup,
} from "@mui/material";
import { useParams } from "react-router";
import axios from "axios";
import CLIModGeneratorToolBar from "./CLIModGeneratorToolBar";
import CLIModGeneratorProfileCommandTree, {
  ExportModViewProfile,
  InitializeCommandTreeByModView,
  ProfileCommandTree,
} from "./CLIModGeneratorProfileCommandTree";
import CLIModGeneratorProfileTabs from "./CLIModGeneratorProfileTabs";
import { CLIModView, CLIModViewProfiles } from "./CLIModuleCommon";

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
  return axios
    .get(
      `/AAZ/Specs/CommandTree/Nodes/aaz/${names.slice(0, -1).join("/")}/Leaves/${names[names.length - 1]}`
    )
    .then((res) => res.data);
}

async function retrieveCommands(
  namesList: string[][]
): Promise<CLISpecsCommand[]> {
  const namesListData = namesList.map((names) => ["aaz", ...names]);
  return axios
    .post(`/AAZ/Specs/CommandTree/Nodes/Leaves`, namesListData)
    .then((res) => res.data);
}

const useSpecsCommandTree: () => (
  namesList: string[][]
) => Promise<CLISpecsCommand[]> = () => {
  const commandCache = React.useRef(
    new Map<string, Promise<CLISpecsCommand>>()
  );

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
        commandCache.current.set(
          uncachedNamesList[0].join("/"),
          commandPromise
        );
        return await Promise.all(promiseResults.concat(commandPromise));
      } else {
        const uncachedCommandsPromise = retrieveCommands(uncachedNamesList);
        uncachedNamesList.forEach((names, idx) => {
          commandCache.current.set(
            names.join("/"),
            uncachedCommandsPromise.then((commands) => commands[idx])
          );
        });
        return (await Promise.all(promiseResults)).concat(
          await uncachedCommandsPromise
        );
      }
    },
    [commandCache]
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
  const [invalidText, setInvalidText] = React.useState<string | undefined>(
    undefined
  );
  const [profiles, setProfiles] = React.useState<string[]>([]);
  const [commandTrees, setCommandTrees] = React.useState<ProfileCommandTrees>(
    {}
  );
  const [selectedProfile, setSelectedProfile] = React.useState<
    string | undefined
  >(undefined);
  const [showGenerateDialog, setShowGenerateDialog] = React.useState(false);
  const [showDraftPowerShellDialog, setShowDraftPowerShellDialog] =
    React.useState(false);

  const fetchCommands = useSpecsCommandTree();

  React.useEffect(() => {
    loadModule();
  }, []);

  const loadModule = async () => {
    try {
      setLoading(true);
      const profiles: string[] = await axios
        .get(`/CLI/Az/Profiles`)
        .then((res) => res.data);

      const modView: CLIModView = await axios
        .get(`/CLI/Az/${params.repoName}/Modules/${params.moduleName}`)
        .then((res) => res.data);

      const simpleTree: CLISpecsSimpleCommandTree = await axios
        .get(`/AAZ/Specs/CommandTree/Simple`)
        .then((res) => res.data);

      Object.keys(modView!.profiles).forEach((profile) => {
        const idx = profiles.findIndex((v) => v === profile);
        if (idx === -1) {
          throw new Error(`Invalid profile ${profile}`);
        }
      });

      const commandTrees = Object.fromEntries(
        profiles.map((profile) => {
          return [
            profile,
            InitializeCommandTreeByModView(
              profile,
              modView!.profiles[profile] ?? null,
              simpleTree
            ),
          ];
        })
      );

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

  const selectedCommandTree = selectedProfile
    ? commandTrees[selectedProfile]
    : undefined;

  const handleBackToHomepage = () => {
    window.open("/?#/cli", "_blank");
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

  const onSelectedProfileTreeUpdate = React.useCallback(
    (
      updater:
        | ((oldTree: ProfileCommandTree) => ProfileCommandTree)
        | ProfileCommandTree
    ) => {
      setCommandTrees((commandTrees) => {
        const selectedCommandTree = commandTrees[selectedProfile!];
        const newTree =
          typeof updater === "function"
            ? updater(selectedCommandTree!)
            : updater;
        return { ...commandTrees, [selectedProfile!]: newTree };
      });
    },
    [selectedProfile]
  );

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
          repoName={params.repoName}
          moduleName={params.moduleName}
          profileCommandTrees={commandTrees}
          open={showDraftPowerShellDialog}
          onClose={handleDraftPowerShellClose}
        />
      )}
      <Backdrop
        sx={{ color: "#fff", zIndex: (theme: any) => theme.zIndex.drawer + 1 }}
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
  const [invalidText, setInvalidText] = React.useState<string | undefined>(
    undefined
  );

  const handleClose = () => {
    props.onClose(false);
  };

  const handleGenerateAll = () => {
    const profiles: CLIModViewProfiles = {};
    Object.values(props.profileCommandTrees).forEach((tree) => {
      profiles[tree.name] = ExportModViewProfile(tree);
    });
    const data = {
      name: props.moduleName,
      profiles: profiles,
    };

    setUpdating(true);
    axios
      .put(`/CLI/Az/${props.repoName}/Modules/${props.moduleName}`, data)
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
    Object.values(props.profileCommandTrees).forEach((tree) => {
      profiles[tree.name] = ExportModViewProfile(tree);
    });
    const data = {
      name: props.moduleName,
      profiles: profiles,
    };

    setUpdating(true);
    axios
      .patch(`/CLI/Az/${props.repoName}/Modules/${props.moduleName}`, data)
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
            <Button onClick={handleGenerateModified}>
              Generate Edited Only
            </Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
}

interface PSModule {
  name: string;
  folder: string | null;
  url: string | null;
}

interface InputType {
  inputValue: string;
  title: string;
}

interface PSSketchProfile {
  resourceProviders: PSSketchResourceProvider[];
}

interface PSSketchResourceProvider {
  swagger: string;
  resources?: PSSketchResource[];
  selected?: boolean;
}

interface PSSketchResource {
  id: string;
  path: string;
  subresources?: string[];
}

function DraftPowerShellDialog(props: {
  repoName: string;
  moduleName: string;
  profileCommandTrees: ProfileCommandTrees;
  open: boolean;
  onClose: (generated: boolean) => void;
}) {
  const [loading, setLoading] = React.useState<boolean>(false);
  const [updating, setUpdating] = React.useState<boolean>(false);
  const [invalidText, setInvalidText] = React.useState<string | undefined>(
    undefined
  );
  const [selectedModule, setSelectedModule] = React.useState<PSModule | null>(
    null
  );

  const [sketchProfile, setSketchProfile] =
    React.useState<PSSketchProfile | null>(null);
  const [moduleOptions, setModuleOptions] = React.useState<PSModule[]>([]);

  const handleClose = () => {
    props.onClose(false);
  };

  const filter = createFilterOptions<PSModule | InputType>();

  const handleDraftPowerShell = () => {
    setUpdating(true);
    // axios
    //     .post(`/CLI/Az/${props.repoName}/Modules/${props.moduleName}/DraftPowerShell`)
    //     .then(() => {
    //         setUpdating(false);
    //         props.onClose(true);
    //     })
  };

  const loadData = React.useCallback(async () => {
    setLoading(true);
    const cliModViewProfile = ExportModViewProfile(
      props.profileCommandTrees["latest"]
    );
    try {
      let response = await axios.get(`/PS/Powershell/Modules`);
      const options = response.data.map((option: any) => {
        return {
          name: option.name,
          folder: option.folder,
          url: option.url,
        };
      });
      setModuleOptions(options);
      response = await axios.post(`/PS/Editor/GenerateSketcheProfile`, {
        cliProfile: cliModViewProfile,
      });
      let profile: PSSketchProfile = response.data;
      profile.resourceProviders.forEach((rp: PSSketchResourceProvider) => {
        rp.selected = true;
      });
      setSketchProfile(profile);
      setLoading(false);
    } catch (err: any) {
      console.error(err);
      if (err.response?.data?.message) {
        const data = err.response!.data!;
        setInvalidText(
          `ResponseError: ${data.message!}: ${JSON.stringify(data.details)}`
        );
      } else {
        setInvalidText(err.message);
      }
      setLoading(false);
    }
  }, [props.profileCommandTrees]);

  React.useEffect(() => {
    if (props.open) {
      loadData();
    } else {
      setLoading(false);
    }
  }, [props.open]);

  const handleResourceProviderChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    index: number
  ) => {
    setSketchProfile((prevProfile) => {
      const newResourceProviders = [...prevProfile!.resourceProviders];
      newResourceProviders[index].selected = event.target.checked;
      return { ...prevProfile!, resourceProviders: newResourceProviders };
    });
  };

  const submitable =
    selectedModule !== null &&
    sketchProfile?.resourceProviders.some((rp) => rp.selected);

  // TODO: need user select the resource providers to generation as click boxes
  return (
    <Dialog disableEscapeKeyDown open={props.open} maxWidth="md" fullWidth>
      <DialogTitle>Draft PowerShell Generation from CLI</DialogTitle>
      <DialogContent>
        {invalidText && (
          <Alert variant="filled" severity="error">
            {" "}
            {invalidText}{" "}
          </Alert>
        )}
        {loading && <CircularProgress />}
        {!loading && (
          <FormControl fullWidth sx={{ mt: 2 }}>
            <Autocomplete
              id="ps-module-select"
              value={selectedModule}
              sx={{ minWidth: 280 }}
              options={moduleOptions}
              onChange={(_event, newValue: any) => {
                if (typeof newValue === "string") {
                  setSelectedModule({
                    name: newValue,
                    folder: null,
                    url: null,
                  });
                } else if (newValue && newValue.inputValue) {
                  setSelectedModule({
                    name: newValue.inputValue,
                    folder: null,
                    url: null,
                  });
                } else {
                  setSelectedModule(newValue as PSModule);
                }
              }}
              filterOptions={(options, params: any) => {
                const filtered = filter(options, params);
                if (
                  params.inputValue !== "" &&
                  -1 === options.findIndex((e) => e.name === params.inputValue)
                ) {
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
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  {option && option.title ? option.title : option.name}
                </Box>
              )}
              selectOnFocus
              clearOnBlur
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="PowerShell Module"
                  inputProps={{
                    ...params.inputProps,
                    placeholder:
                      "The folder to generate the Autorest code, e.g. ServiceName/ServiceName.Autorest",
                    autoComplete: "new-password", // disable autocomplete and autofill
                  }}
                />
              )}
            ></Autocomplete>
            <FormLabel sx={{ mt: 2 }}>Resource Providers</FormLabel>
            {sketchProfile && (
              <FormGroup>
                {sketchProfile.resourceProviders.map((rp, index) => (
                  <FormControlLabel
                    key={index}
                    control={
                      <Checkbox
                        checked={rp.selected}
                        onChange={(e) => handleResourceProviderChange(e, index)}
                      />
                    }
                    label={rp.swagger}
                  />
                ))}
              </FormGroup>
            )}
          </FormControl>
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
            <Button
              onClick={handleDraftPowerShell}
              disabled={!submitable || loading}
            >
              Draft
            </Button>
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
