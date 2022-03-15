import React, { Component, useState } from "react";
import { Button, Container, Nav, Navbar } from "react-bootstrap";
import { useParams } from "react-router-dom";
import axios from "axios";
import styles from "./TreeView/App.module.css";
import { NodeModel, Tree } from "@minoru/react-dnd-treeview";
import { CheckData } from "./TreeView/types";
import { CheckNode } from "./TreeView/CheckNode";

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

// type Reference = {
//   name?: string;
//   commandGroups: CommandGroups;
//   commands: Commands;
// };
//
// type Generation = {
//   [name: string]: Reference;
// };

type GeneratorState = {
  currRepo: "Azure CLI" | "Azure CLI Extension";
  moduleName: string;
  toBeGenerated: CommandGroups;
  profiles: string[];
  currProfile: string;
  treeData: TreeNode[];
  currIdx: number;
  selectedIdx: number[];
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
      selectedIdx: [],
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
    console.log(this.state.treeData);
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
          if (commands) {
            const versionList = commands[commandName]["versions"];
            versionList.map((version) => versions.push(version["name"]));
          }
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

    const getNodeData = (path: string) => {
      return axios
        .post(`/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${path}/Transfer`)
        .then((res) => {
          return res.data;
        })
        .catch((err) => console.log(err));
    };

    const getLeafData = (path: string, command: string, version: string) => {
      return axios
        .post(
          `/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${path}/Leaves/${command}/Versions/${version}/Transfer`
        )
        .then((res) => {
          return res.data;
        })
        .catch((err) => console.log(err));
    };

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

    const getReference = (namePath: string[]) => {
      let reference = this.state.toBeGenerated[this.state.currProfile];
      namePath.slice(0, -1).forEach((item, idx) => {
        const currPath = namePath.slice(0, idx + 1).join("/");
        const data = getNodeData(currPath);
        if (!reference.hasOwnProperty("commandGroups")) {
          let element: any = {};
          element[item] = data;
          reference["commandGroups"] = element;
          reference = reference["commandGroups"][item];
        } else if (!reference["commandGroups"].hasOwnProperty(item)) {
          let element: any = reference["commandGroups"];
          element[item] = data;
          reference["commandGroups"] = element;
          reference = reference["commandGroups"][item];
        } else {
          reference = reference["commandGroups"][item];
        }
      });
      return reference;
    };

    const handleSelect = (node: NodeModel) => {
      const item = selectedNodes.find((n) => n.id === node.id);

      if (!item) {
        setSelectedNodes([...selectedNodes, node]);
        const namePath = getNamePath(node);
        const path = namePath.slice(0, -1).join("/");
        const command = namePath[namePath.length - 1];
        const currNode = this.state.treeData[Number(node.id) - 1];
        const version = btoa(String(currNode.data.currVersion))
        const data = getLeafData(path, command, version)
        let commandRef = getReference(namePath);
        if (!commandRef.hasOwnProperty("commands")) {
          let element: any = {}
          element[command] = data
          commandRef["commands"] = element
        } else {
          let element: any = commandRef["commands"]
          element[command] = data;
          commandRef["commands"] = element
        }
        console.log(this.state.toBeGenerated)
      } else {
        setSelectedNodes(selectedNodes.filter((n) => n.id !== node.id));
      }
    };

    const handleChange = (version: string, node: NodeModel) => {
      // let currNode = this.state.treeData[Number(node.id) - 1];
      // currNode.data.currVersion = version;
      //
      // const namePath = getNamePath(node);
      // let currLocation: Profile | CommandGroup =
      //   this.state.toBeGenerated[this.state.currProfile];
      // namePath.slice(0, -1).forEach((name) => {
      //   if (currLocation.commandGroups) {
      //     currLocation = currLocation["commandGroups"][name];
      //   }
      // });
      //
      // if (currLocation.commands) {
      //   currLocation["commands"][namePath.slice(-1)[0]]["version"] = version;
      // }
    };

    const handleDrop = () => {};

    return (
      <div className={styles.app}>
        <Tree
          tree={this.state.treeData}
          rootId={0}
          render={(node: NodeModel<CheckData>, { depth, isOpen, onToggle }) => (
            <CheckNode
              node={node}
              depth={depth}
              isOpen={isOpen}
              isSelected={!!selectedNodes.find((n) => n.id === node.id)}
              onToggle={onToggle}
              onSelect={handleSelect}
              onChange={handleChange}
            />
          )}
          onDrop={handleDrop}
          classes={{
            root: styles.treeRoot,
            draggingSource: styles.draggingSource,
            dropTarget: styles.dropTarget,
          }}
        />
      </div>
    );
  };

  render() {
    return (
      <div>
        <this.displayNavbar />
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
export type { TreeNode };
