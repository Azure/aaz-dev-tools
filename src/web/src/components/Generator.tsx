import React, {Component, useState} from "react";
import {Button, Container, Nav, Navbar} from "react-bootstrap";
import {useParams} from "react-router-dom";
import axios from "axios";
import styles from "./TreeView/App.module.css";
import {NodeModel, Tree} from "@minoru/react-dnd-treeview";
import {CheckData} from "./TreeView/types";
import {CheckNode} from "./TreeView/CheckNode";

const repoMap = {
  "Azure CLI": "Main",
  "Azure CLI Extension": "Extension",
};

type Version = {
  name: string;
  resources: {};
};

type Command = {
  help: { short: string };
  names: string[];
  version: string;
  versions: Version[];
};

type Commands = {
  [name: string]: Command;
};

type CommandGroup = {
  commandGroups: CommandGroups;
  commands?: Commands;
  names: string[];
  help?: {};
  examples?: {};
  argGroups?: {};
};

type CommandGroups = {
  [name: string]: CommandGroup;
};

type TreeNode = {
  id: number;
  parent: number;
  droppable: boolean;
  text: string;
  data: {
    type: string;
    currVersion?: string;
    versions?: string[];
  };
};

type ExampleTye = {
  commands: string[];
  name: string;
};

type HelpType = {
  short: string;
  examples?: ExampleTye[];
};

type RegisterType = {
  stage: string;
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

type ResourceType = {
  id: string;
  plane: string;
  version: string;
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

type GeneratorState = {
  currRepo: "Azure CLI" | "Azure CLI Extension";
  moduleName: string;
  toBeGenerated: Nodes;
  profiles: string[];
  currProfile: string;
  treeData: TreeNode[];
  currIdx: number;
};

class Generator extends Component<any, GeneratorState> {
  constructor(props: any) {
    super(props);
    this.state = {
      currRepo: this.props.params.currRepo,
      moduleName: this.props.params.moduleName,
      toBeGenerated: {},
      profiles: [],
      currProfile: "",
      treeData: [],
      currIdx: 0,
    };
  }

  componentDidMount() {
    axios.get("/CLI/Az/Profiles").then((res) => {
      this.setState({ profiles: res.data });
      this.setState({ currProfile: "latest" });
    });

    axios.get(`/CLI/Az/Main/Modules/${this.state.moduleName}`).then((res) => {
      this.setState({ toBeGenerated: res.data["profiles"] });
    });

    const url = `/AAZ/Specs/CommandTree/Nodes/aaz/${this.state.moduleName}`;
    axios.get(url).then((res) => {
      let combinedData: CommandGroups = {};
      const moduleName = this.state.moduleName;
      combinedData[moduleName] = res.data;
      combinedData[moduleName]["names"] = [moduleName];
      let commandGroups: CommandGroups = combinedData;
      if (!commandGroups) {
        return;
      }
      let depth = 0;
      return this.parseCommandGroup(depth, 0, commandGroups).then(() => {
        return Promise.resolve();
      });
    });
    console.log(this.state.treeData)
  }

  parseCommandGroup = (
    depth: number,
    parentIdx: number,
    commandGroups?: CommandGroups
  ) => {
    if (!commandGroups) {
      return Promise.resolve();
    }

    let totalPromise: Promise<any>[] = Object.keys(commandGroups).map(
      (commandGroupName) => {
        this.setState({ currIdx: this.state.currIdx + 1 });
        let treeNode: TreeNode = {
          id: this.state.currIdx,
          parent: parentIdx,
          text: commandGroupName,
          droppable: true,
          data: { type: "CommandGroup" },
        };
        this.state.treeData.push(treeNode);

        let commandGroupIdx = this.state.currIdx;
        let commandGroupPromise: Promise<any> = this.parseCommandGroup(
          depth + 1,
          this.state.currIdx,
          commandGroups[commandGroupName].commandGroups
        );
        let commands = commandGroups[commandGroupName].commands;
        if (!commands) {
          return commandGroupPromise;
        }

        // eslint-disable-next-line array-callback-return
        let commandPromises = Object.keys(commands).map((commandName) => {
          this.setState({ currIdx: this.state.currIdx + 1 });
          let versions: string[] = [];
          const versionList = commands![commandName]["versions"];
          versionList.map((version) => versions.push(version["name"]));
          let treeNode: TreeNode = {
            id: this.state.currIdx,
            parent: commandGroupIdx,
            text: commandName,
            droppable: false,
            data: {
              type: "Command",
              currVersion: versions[0],
              versions: versions,
            },
          };
          this.state.treeData.push(treeNode);
        });
        return Promise.all([commandGroupPromise, ...commandPromises]);
      }
    );
    return Promise.all(totalPromise);
  };

  displayNavbar = () => {
    const handleClick = (event: any) => {
      const profileName = event.target.text;
      this.setState({ currProfile: profileName });
    };

    const handleGen = () => {
      axios
        .put(
          `/CLI/Az/${repoMap[this.state.currRepo]}/Modules/${
            this.state.moduleName
          }`,
          { profiles: this.state.toBeGenerated }
        )
        .then(() => {})
        .catch((err) => {
          console.error(err.response);
        });
    };

    return (
      <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
        <Container>
          <Navbar.Brand>{this.state.moduleName}</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="me-auto">
              {this.state.profiles.map((profile: string, idx) => {
                return (
                  <Nav.Link
                    key={idx}
                    href={`#${profile}`}
                    onClick={handleClick}
                  >
                    {profile}
                  </Nav.Link>
                );
              })}
            </Nav>
            <Button onClick={handleGen}>Generate</Button>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    );
  };

  displayCommandTree = () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [selectedNodes, setSelectedNodes] = useState<NodeModel[]>([]);

    const getNamePath = (node: NodeModel) => {
      let namePath = [node.text];
      let currId = Number(node.parent);
      while (currId !== 0) {
        const currNode = this.state.treeData[currId - 1];
        namePath.unshift(currNode.text);
        currId = currNode.parent;
      }
      return namePath;
    };

    const prepareNodes = (namePath: string[]) => {
      let currLocation = this.state.toBeGenerated[this.state.currProfile];
      const promises = namePath.slice(0, -1).map((item, idx) => {
        const currPath = namePath.slice(0, idx + 1).join("/");
        return axios
          .post(`/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${currPath}/Transfer`)
          .then((res) => {
            const data = res.data;
            if (!currLocation.hasOwnProperty("commandGroups")) {
              let element: Nodes = {};
              element[item] = data;
              currLocation["commandGroups"] = element;
              currLocation = currLocation["commandGroups"][item];
            } else {
              if (!currLocation["commandGroups"]!.hasOwnProperty(item)) {
                let element: Nodes = currLocation["commandGroups"]!;
                element[item] = data;
                currLocation["commandGroups"] = element;
                currLocation = currLocation["commandGroups"][item];
              } else {
                currLocation = currLocation["commandGroups"]![item];
              }
            }
          })
          .catch((err) => console.log(err));
      });
      return Promise.all(promises);
    };

    const insertLeaf = (path: string, command: string, version: string) => {
      let currLocation = this.state.toBeGenerated[this.state.currProfile];
      path.split("/").forEach((item) => {
        currLocation = currLocation["commandGroups"]![item];
      });
      axios
        .post(
          `/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${path}/Leaves/${command}/Versions/${version}/Transfer`
        )
        .then((res) => {
          const data = res.data;
          if (!currLocation.hasOwnProperty("commands")) {
            let element: Leaves = {};
            element[command] = data;
            currLocation["commands"] = element;
          } else {
            let element: Leaves = currLocation["commands"]!;
            element[command] = data;
            currLocation["commands"] = element;
          }
        })
        .catch((err) => console.log(err));
    };

    const removeNodes = (namePath: string[]) => {
      const nodeName = namePath[namePath.length - 1];
      let currLocation = this.state.toBeGenerated[this.state.currProfile];
      namePath.slice(0, -1).forEach((item) => {
        currLocation = currLocation["commandGroups"]![item];
      });
      delete currLocation["commandGroups"]![nodeName];
      if (Object.keys(currLocation["commandGroups"]!).length === 0) {
        delete currLocation["commandGroups"];
        return true;
      } else {
        return false;
      }
    };

    const handleSelect = (node: NodeModel) => {
      const item = selectedNodes.find((n) => n.id === node.id);

      if (!item) {
        setSelectedNodes([...selectedNodes, node]);

        const namePath = getNamePath(node);
        prepareNodes(namePath).then(() => {
          const path = namePath.slice(0, -1).join("/");
          const currNode = this.state.treeData[Number(node.id) - 1];
          const version = btoa(String(currNode.data.currVersion));
          insertLeaf(path, node.text, version)
        });
      } else {
        setSelectedNodes(selectedNodes.filter((n) => n.id !== node.id));

        const namePath = getNamePath(node);
        let currLocation = this.state.toBeGenerated[this.state.currProfile];
        namePath.slice(0, -1).forEach((item) => {
          currLocation = currLocation["commandGroups"]![item];
        });
        delete currLocation["commands"]![node.text];

        if (Object.keys(currLocation["commands"]!).length === 0) {
          delete currLocation["commands"];
          for (let idx = namePath.length - 1; idx > 0; idx--) {
            if (!removeNodes(namePath.slice(0, idx))) {
              break;
            }
          }
        }
      }
      console.log(this.state.toBeGenerated);
    };

    const handleChange = (node: NodeModel, version: string) => {
      let currNode = this.state.treeData[Number(node.id) - 1];
      currNode.data.currVersion = version;

      const namePath = getNamePath(node);
      let currLocation = this.state.toBeGenerated[this.state.currProfile];
      namePath.slice(0, -1).forEach((item) => {
        currLocation = currLocation["commandGroups"]![item];
      });
      currLocation["commands"]![node.text]["version"] = version;
    };

    const handleDrop = () => {};

    const isGenerated = (node: TreeNode) => {
      let namePath = [];
      let currId = Number(node.parent);
      while (currId !== 0) {
        const currNode = this.state.treeData[currId - 1];
        namePath.unshift(currNode.text);
        currId = currNode.parent;
      }
      let currLocation = this.state.toBeGenerated[this.state.currProfile];
      try {
        namePath.forEach((item) => {
          currLocation = currLocation["commandGroups"]![item];
        });
        node.data.currVersion = currLocation["commands"]![node.text]["version"]
      } catch (e: unknown) {
        return false;
      }
      return true;
    };

    const handleClick = (event: any) => {
      const profileName = event.target.text;
      this.setState({ currProfile: profileName });
      const selectedNodes = this.state.treeData
          .filter((node) => node.data.type === "Command")
          .filter((node) => isGenerated(node));
      setSelectedNodes(selectedNodes);
      console.log(this.state.treeData)
      console.log(this.state.toBeGenerated)
    };

    const handleGen = () => {
      axios
          .put(
              `/CLI/Az/${repoMap[this.state.currRepo]}/Modules/${
                  this.state.moduleName
              }`,
              { profiles: this.state.toBeGenerated }
          )
          .then(() => {})
          .catch((err) => {
            console.error(err.response);
          });
    };

    return (
      <div className={styles.app}>
        <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
          <Container>
            <Navbar.Brand>{this.state.moduleName}</Navbar.Brand>
            <Navbar.Toggle aria-controls="responsive-navbar-nav" />
            <Navbar.Collapse id="responsive-navbar-nav">
              <Nav className="me-auto">
                {this.state.profiles.map((profile: string, idx) => {
                  return (
                      <Nav.Link
                          key={idx}
                          // href={`#${profile}`}
                          onClick={handleClick}
                      >
                        {profile}
                      </Nav.Link>
                  );
                })}
              </Nav>
              <Button onClick={handleGen}>Generate</Button>
            </Navbar.Collapse>
          </Container>
        </Navbar>
        {/*<Tree*/}
        {/*  tree={this.state.treeData}*/}
        {/*  rootId={0}*/}
        {/*  render={(node: NodeModel<CheckData>, { depth, isOpen, onToggle }) => (*/}
        {/*    <CheckNode*/}
        {/*      node={node}*/}
        {/*      depth={depth}*/}
        {/*      isOpen={isOpen}*/}
        {/*      isSelected={!!selectedNodes.find((n) => n.id === node.id)}*/}
        {/*      onToggle={onToggle}*/}
        {/*      onSelect={handleSelect}*/}
        {/*      onChange={handleChange}*/}
        {/*    />*/}
        {/*  )}*/}
        {/*  onDrop={handleDrop}*/}
        {/*  classes={{*/}
        {/*    root: styles.treeRoot,*/}
        {/*    draggingSource: styles.draggingSource,*/}
        {/*    dropTarget: styles.dropTarget,*/}
        {/*  }}*/}
        {/*/>*/}
      </div>
    );
  };

  render() {
    return (
      <div>
        <this.displayCommandTree />
      </div>
    );
  }
}

const GeneratorWrapper = (props: any) => {
  const params = useParams();
  return <Generator params={params} {...props} />;
};

export { GeneratorWrapper as Generator };
