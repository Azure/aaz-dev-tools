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
  versions: Version[];
};

type Commands = {
  [name: string]: Command;
};

type CommandGroup = {
  commandGroups?: CommandGroups;
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
    versions?: string[];
  };
};

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
            data: { type: "Command", versions: versions },
          };
          this.state.treeData.push(treeNode);
        });
        return Promise.all([commandGroupPromise, ...commandPromises]);
      }
    );
    return Promise.all(totalPromise);
  };

  // getCommand = (
  //   currentIndex: number,
  //   namesPath: string,
  //   commandName: string
  // ) => {
  //   let url = `/AAZ/Specs/CommandTree/Nodes/aaz/${namesPath}/Leaves/${commandName}`;
  //   return axios
  //     .get(url)
  //     .then((res) => {
  //       return res.data;
  //     })
  //     .catch((err) => console.log(err));
  // };

  displayNavbar = () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [selectedNodes, setSelectedNodes] = useState<NodeModel[]>([]);

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
    const handleDrop = () => {};
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [selectedNodes, setSelectedNodes] = useState<NodeModel[]>([]);

    const handleSelect = (node: NodeModel) => {
      const item = selectedNodes.find((n) => n.id === node.id);

      if (!item) {
        setSelectedNodes([...selectedNodes, node]);
        const version = "2021-12-01";
        let namePath = [node.text];
        let currId = Number(node.parent);
        while (currId !== 0) {
          const currNode = this.state.treeData[currId - 1];
          namePath.unshift(currNode.text);
          currId = currNode.parent;
        }
        let profile = this.state.toBeGenerated[this.state.currProfile];
        namePath.slice(0, -1).forEach((item, idx) => {
          const currPath = namePath.slice(0, idx + 1).join("/");
          axios
            .post(
              `/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${currPath}/Transfer`
            )
            .then((res) => {
              let currItem: CommandGroups = {};
              currItem[item] = res.data;
              profile["commandGroups"] = currItem;
              profile = profile["commandGroups"][item];
            });
        });
        const currPath = namePath.slice(0, -1).join("/");
        const currCmdName = namePath.slice(-1)[0];
        const url = `/CLI/Az/AAZ/Specs/CommandTree/Nodes/aaz/${currPath}/Leaves/${currCmdName}/Versions/${btoa(
          version
        )}/Transfer`;
        axios.post(url).then((res) => {
          let currItem: Commands = {};
          currItem[currCmdName] = res.data;
          profile["commands"] = currItem;
        });
      } else {
        setSelectedNodes(selectedNodes.filter((n) => n.id !== node.id));
      }
    };

    const handleClear = (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        setSelectedNodes([]);
      }
    };

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
            />
          )}
          onDrop={handleDrop}
          classes={{
            root: styles.treeRoot,
            draggingSource: styles.draggingSource,
            dropTarget: styles.dropTarget,
          }}
          rootProps={{
            onClick: handleClear,
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
