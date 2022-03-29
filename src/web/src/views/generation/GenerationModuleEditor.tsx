import * as React from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Drawer,
  LinearProgress,
  Toolbar,
} from "@mui/material";
import { useParams } from "react-router";
import GenerationProfileTab from "./GenerationProfileTab";
import GenerationCommandTree from "./GenerationCommandTree";
import axios from "axios";
import { NodeModel } from "@minoru/react-dnd-treeview";
import { CheckData } from "../../components/TreeView/types";
import GenerationModuleEditorToolBar from "./GenerationModuleEditorToolBar";
import { Alert } from "reactstrap";

type Version = {
  examples: ExampleType;
  name: string;
  resources: ResourceType[];
  stage: string;
};

type Command = {
  help: { short: string };
  names: string[];
  versions: Version[];
};

type Commands = {
  [name: string]: Command;
};

type CommandGroup = {
  commandGroups?: CommandGroups;
  commands?: Commands;
  help: HelpType;
  names: string[];
};

type CommandGroups = {
  [name: string]: CommandGroup;
};

type RegisterType = {
  stage: string;
};

type ResourceType = {
  id: string;
  plane: string;
  version: string;
};

type ExampleType = {
  commands: string[];
  name: string;
};

type HelpType = {
  short: string;
  examples?: ExampleType[];
};

type LeafType = {
  help: HelpType;
  names: string[];
  registerInfo: RegisterType;
  resources: ResourceType[];
  stage: string;
  version: string;
};

type Leaves = {
  [name: string]: LeafType;
};

type NodeType = {
  help: HelpType;
  names: string[];
  registerInfo: RegisterType;
  commandGroups?: Nodes;
  commands?: Leaves;
};

type Nodes = {
  [name: string]: NodeType;
};

interface GenerationModuleEditorProps {
  params: {
    repoName: string;
    moduleName: string;
  };
}

interface GenerationModuleEditorState {
  repoName: string;
  moduleName: string;
  profiles: string[];
  profileIndex: number;
  currentIndex: number;
  initialTreeData: NodeModel<CheckData>[];
  treeData: NodeModel<CheckData>[];
  toBeGenerated: Nodes;
  selectedNodes: NodeModel<CheckData>[];
  showGenerateDialog: boolean;
}

class GenerationModuleEditor extends React.Component<
  GenerationModuleEditorProps,
  GenerationModuleEditorState
> {
  constructor(props: GenerationModuleEditorProps) {
    super(props);
    this.state = {
      repoName: this.props.params.repoName,
      moduleName: this.props.params.moduleName,
      profiles: [],
      profileIndex: 0,
      currentIndex: 0,
      initialTreeData: [],
      treeData: [],
      toBeGenerated: {},
      selectedNodes: [],
      showGenerateDialog: false,
    };
  }

  componentDidMount() {
    this.initialModuleEditor();
  }

  initialModuleEditor = () => {
    axios
      .get("/CLI/Az/Profiles")
      .then((res) => {
        this.setState({ profiles: res.data }, () => {
          this.loadCommandTree();
        });
      })
      .catch((err) => {
        console.error(err.response);
      });
  };

  loadCommandTree = () => {
    axios
      .get(`/AAZ/Specs/CommandTree/Nodes/aaz`)
      .then((res) => {
        if (!res.data) {
          return;
        }
        let combinedData: CommandGroups = {};
        const moduleName = "az";
        combinedData[moduleName] = res.data;
        combinedData[moduleName]["names"] = ["az"];

        let depth = 0;
        this.parseCommandTree(depth, 0, combinedData).then(() => {
          this.setState({ treeData: this.state.initialTreeData }, () => {
            this.loadLocalCommands();
          });
        });
      })
      .catch((err) => {
        console.error(err.response);
      });
  };

  loadLocalCommands = () => {
    axios
      .get(`/CLI/Az/${this.state.repoName}/Modules/${this.state.moduleName}`)
      .then((res) => {
        this.setState({ toBeGenerated: res.data["profiles"] }, () => {
          const selectedNodes = this.state.treeData
            .filter((node) => node.data!.type === "Command")
            .filter((node) => this.isGenerated(node));
          this.setState({ selectedNodes: selectedNodes });
        });
      })
      .catch((err) => {
        console.error(err.response);
      });
  };

  parseCommandTree = (
    depth: number,
    parentIndex: number,
    commandGroups?: CommandGroups
  ) => {
    if (!commandGroups) {
      return Promise.resolve();
    }
    let totalPromise: Promise<any>[] = Object.keys(commandGroups).map(
      (groupName) => {
        this.setState({ currentIndex: this.state.currentIndex + 1 });
        let treeNode: NodeModel<CheckData> = {
          id: this.state.currentIndex,
          parent: parentIndex,
          text: groupName,
          droppable: true,
          data: { type: "CommandGroup", versions: [], versionIndex: -1 },
        };
        this.state.initialTreeData.push(treeNode);
        let commandGroupIndex = this.state.currentIndex;
        let commandGroupPromise: Promise<any> = this.parseCommandTree(
          depth + 1,
          this.state.currentIndex,
          commandGroups[groupName]["commandGroups"]
        );

        let commands = commandGroups[groupName]["commands"];
        if (!commands) {
          return commandGroupPromise;
        }
        // eslint-disable-next-line array-callback-return
        let commandPromises = Object.keys(commands).map((commandName) => {
          this.setState({ currentIndex: this.state.currentIndex + 1 });
          let versions: string[] = [];
          const versionList = commands![commandName]["versions"];
          versionList.map((version) => versions.push(version["name"]));
          let treeNode: NodeModel<CheckData> = {
            id: this.state.currentIndex,
            parent: commandGroupIndex,
            text: commandName,
            droppable: false,
            data: {
              type: "Command",
              versions: versions,
              versionIndex: 0,
            },
          };
          this.state.initialTreeData.push(treeNode);
        });
        return Promise.all([commandGroupPromise, ...commandPromises]);
      }
    );
    return Promise.all(totalPromise);
  };

  getNamePath = (node: NodeModel<CheckData>) => {
    let namePath = [node.text];
    let currentId = node.parent;
    while (currentId !== 0) {
      const currNode = this.state.treeData[Number(currentId) - 1];
      namePath.unshift(currNode.text);
      currentId = currNode.parent;
    }
    return namePath.slice(1);
  };

  getProfileEntry = () => {
    const profileName = this.state.profiles[this.state.profileIndex];
    return this.state.toBeGenerated[profileName];
  };

  isGenerated = (node: NodeModel<CheckData>) => {
    const namePath = this.getNamePath(node);
    let currentPointer = this.getProfileEntry();
    try {
      namePath.slice(0, -1).forEach((item) => {
        currentPointer = currentPointer["commandGroups"]![item];
      });
      const versionName = currentPointer["commands"]![node.text]["version"];
      node.data!.versionIndex = node.data!.versions.indexOf(versionName);
    } catch (e: unknown) {
      return false;
    }
    return true;
  };

  refreshVersionInfo = () => {
    this.state.treeData.forEach((node) => {
      node.data!.versionIndex = 0;
    });
  };

  async prepareNodes(namePath: string[]) {
    let currentPointer = this.getProfileEntry();
    for (let idx = 0; idx < namePath.length - 1; idx++) {
      const name = namePath[idx];
      const currentPath = namePath.slice(0, idx + 1).join("/");
      await axios
        .post(`/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${currentPath}/Transfer`)
        // eslint-disable-next-line no-loop-func
        .then((res) => {
          const data = res.data;
          if (!currentPointer.hasOwnProperty("commandGroups")) {
            let element: Nodes = {};
            element[name] = data;
            currentPointer["commandGroups"] = element;
            currentPointer = currentPointer["commandGroups"][name];
          } else {
            if (!currentPointer["commandGroups"]!.hasOwnProperty(name)) {
              let element: Nodes = currentPointer["commandGroups"]!;
              element[name] = data;
              currentPointer["commandGroups"] = element;
              currentPointer = currentPointer["commandGroups"][name];
            } else {
              currentPointer = currentPointer["commandGroups"]![name];
            }
          }
        })
        .catch((err) => console.log(err));
    }
  }

  insertLeaf = (path: string, command: string, version: string) => {
    let currentPointer = this.getProfileEntry();
    path.split("/").forEach((name) => {
      currentPointer = currentPointer["commandGroups"]![name];
    });
    axios
      .post(
        `/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${path}/Leaves/${command}/Versions/${version}/Transfer`
      )
      .then((res) => {
        const data = res.data;
        if (!currentPointer.hasOwnProperty("commands")) {
          let element: Leaves = {};
          element[command] = data;
          currentPointer["commands"] = element;
        } else {
          let element: Leaves = currentPointer["commands"]!;
          element[command] = data;
          currentPointer["commands"] = element;
        }
      })
      .catch((err) => console.log(err));
  };

  removeNodes = (namePath: string[]) => {
    const nodeName = namePath[namePath.length - 1];
    let currentPointer = this.getProfileEntry();
    namePath.slice(0, -1).forEach((name) => {
      currentPointer = currentPointer["commandGroups"]![name];
    });
    delete currentPointer["commandGroups"]![nodeName];
    if (Object.keys(currentPointer["commandGroups"]!).length === 0) {
      delete currentPointer["commandGroups"];
      return true;
    } else {
      return false;
    }
  };

  handleBackToHomepage = () => {
    window.location.href = `/?#/generation`;
  };

  handleGenerate = () => {
    this.setState({ showGenerateDialog: true });
  };

  handleGenerationClose = (generated: boolean) => {
    this.setState({ showGenerateDialog: false });
  };

  handleProfileChange = (event: React.SyntheticEvent, newValue: number) => {
    this.setState({ profileIndex: newValue }, () => {
      this.refreshVersionInfo();
      const selectedNodes = this.state.treeData
        .filter((node) => node.data!.type === "Command")
        .filter((node) => this.isGenerated(node));
      this.setState({ selectedNodes: selectedNodes });
    });
  };

  handleSelect = (node: NodeModel<CheckData>) => {
    const currentNode = this.state.selectedNodes.find((n) => n.id === node.id);
    if (!currentNode) {
      this.state.selectedNodes.push(node);
      const namePath = this.getNamePath(node);
      this.prepareNodes(namePath).then(() => {
        const path = namePath.slice(0, -1).join("/");
        const currentNode = this.state.treeData[Number(node.id) - 1];
        const versionIndex = currentNode.data!.versionIndex;
        const version = btoa(currentNode.data!.versions[versionIndex]);
        this.insertLeaf(path, node.text, version);
      });
    } else {
      this.setState({
        selectedNodes: this.state.selectedNodes.filter((n) => n.id !== node.id),
      });
      const namePath = this.getNamePath(node);
      let currentPointer = this.getProfileEntry();
      namePath.slice(0, -1).forEach((name) => {
        currentPointer = currentPointer["commandGroups"]![name];
      });
      delete currentPointer["commands"]![node.text];

      if (Object.keys(currentPointer["commands"]!).length === 0) {
        delete currentPointer["commands"];
        for (let idx = namePath.length - 1; idx > 0; idx--) {
          if (!this.removeNodes(namePath.slice(0, idx))) {
            break;
          }
        }
      }
    }
  };

  handleVersionChange = (node: NodeModel<CheckData>, currentVersion: string) => {
    let changeNode = this.state.treeData[Number(node.id) - 1];
    changeNode.data!.versionIndex = changeNode.data!.versions.indexOf(currentVersion);
    const namePath = this.getNamePath(node);
    let currentPointer = this.getProfileEntry();
    namePath.slice(0, -1).forEach((name) => {
      currentPointer = currentPointer["commandGroups"]![name];
    });
    delete currentPointer["commands"]![node.text]
    const path = namePath.slice(0, -1).join("/");
    const version = btoa(currentVersion)
    this.insertLeaf(path, node.text, version);
  };

  render() {
    const { moduleName, showGenerateDialog } = this.state;
    return (
      <React.Fragment>
        <GenerationModuleEditorToolBar
          moduleName={moduleName}
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
            <GenerationProfileTab
              value={this.state.profileIndex}
              profiles={this.state.profiles}
              onChange={this.handleProfileChange}
            />
          </Drawer>
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 1,
            }}
          >
            <Toolbar sx={{ flexShrink: 0 }} />
            {this.state.treeData.length !== 0 && (
              <GenerationCommandTree
                treeData={this.state.treeData}
                selectedNodes={this.state.selectedNodes}
                onSelect={this.handleSelect}
                onChange={this.handleVersionChange}
              />
            )}
          </Box>
        </Box>
        {showGenerateDialog && (
          <GenerationModuleEditorDialog
            url={`/CLI/Az/${this.state.repoName}/Modules/${this.state.moduleName}`}
            data={{ profiles: this.state.toBeGenerated }}
            open={true}
            onClose={this.handleGenerationClose}
          />
        )}
      </React.Fragment>
    );
  }
}

function GenerationModuleEditorDialog(props: {
  url: string;
  data: any;
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

  const handleGenerate = () => {
    setUpdating(true);
    axios
      .put(props.url, props.data)
      .then(() => {
        setUpdating(false);
        props.onClose(true);
      })
      .catch((err) => {
        console.error(err.response);
        if (err.resource?.message) {
          setInvalidText(`ResponseError: ${err.resource!.message!}`);
        }
        setUpdating(false);
      });
  };

  return (
    <Dialog disableEscapeKeyDown open={props.open}>
      <DialogTitle>Generate CLI commands to local disk</DialogTitle>
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
            <LinearProgress color="info" />
          </Box>
        )}
        {!updating && (
          <React.Fragment>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleGenerate}>Confirm</Button>
          </React.Fragment>
        )}
      </DialogActions>
    </Dialog>
  );
}

const GenerationModuleEditorWrapper = (props: any) => {
  const params = useParams();
  return <GenerationModuleEditor params={params} {...props} />;
};

export { GenerationModuleEditorWrapper as GenerationModuleEditor };
